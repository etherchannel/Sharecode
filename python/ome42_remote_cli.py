"""
Run RACADM commands against systems managed by OpenManage Enterprise (OME) via JobService.

USAGE OVERVIEW
Mandatory arguments:
    -i <OME IP/Host>
    -u <Username>
    -p <Password>
    -c <RACADM command>

Optional arguments:
    -g <Group Name>            Scope to devices in a specific OME group
    --insecure                 Disable TLS certificate verification (self-signed certs)
    --poll-interval <seconds>  Seconds between job status polls (default: 5)
    --max-wait <seconds>       Max seconds to wait per job before timing out (default: 120)

MINIMAL EXAMPLES
    # All managed iDRAC systems
    python ome42_remote_cli.py -i 192.168.159.142 -u admin -p P@ssw0rd -c getsysinfo

    # Only devices in a named group
    python ome42_remote_cli.py -i 192.168.159.142 -u admin -p P@ssw0rd -c getsysinfo -g "All Devices"

FULL / EXPLICIT EXAMPLES
    # Specify all tunables (longer wait, slower polling, ignore cert warnings)
    python ome42_remote_cli.py -i 192.168.159.142 -u admin -p P@ssw0rd -c getsysinfo -g "All Devices" --poll-interval 10 --max-wait 300 --insecure

NOTES
    - Omit --insecure if the OME certificate is trusted.
    - Increase --max-wait for long‑running commands (e.g., inventory collection).
    - Decrease --poll-interval to get faster feedback at the cost of more API calls.
    - Exit code 0: all device jobs succeeded; 2: at least one failure or unrecoverable error.
"""

import argparse
import json
import sys
import time
import warnings
from typing import Any, Dict, List, Optional, Tuple

import requests
from requests.adapters import HTTPAdapter


def build_session(insecure: bool) -> requests.Session:
    session = requests.Session()
    adapter = HTTPAdapter(pool_connections=20, pool_maxsize=50)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    session.verify = not insecure
    if insecure:
        warnings.filterwarnings("ignore")
    return session


def authenticate(session: requests.Session, ome_ip: str, username: str, password: str, timeout: int = 15) -> str:
    url = f"https://{ome_ip}/api/SessionService/Sessions"
    headers = {"Content-Type": "application/json"}
    payload = {"UserName": username, "Password": password, "SessionType": "API"}
    resp = session.post(url, headers=headers, data=json.dumps(payload), timeout=timeout, auth=(username, password))
    if resp.status_code != 201:
        raise RuntimeError(f"Authentication failed (HTTP {resp.status_code}): {resp.text}")
    return resp.headers.get("X-Auth-Token")


def request_with_token(
    session: requests.Session,
    method: str,
    url: str,
    *,
    token: str,
    ome_ip: str,
    username: str,
    password: str,
    timeout: int = 30,
    retry_on_401: bool = True,
    **kwargs: Any,
) -> Tuple[requests.Response, str]:
    headers = kwargs.pop("headers", {}) or {}
    headers = {**headers, "Content-Type": "application/json", "X-Auth-Token": token}
    resp = session.request(method, url, headers=headers, timeout=timeout, **kwargs)
    if resp.status_code == 401 and retry_on_401:
        # refresh token and retry once
        new_token = authenticate(session, ome_ip, username, password, timeout=15)
        headers["X-Auth-Token"] = new_token
        resp = session.request(method, url, headers=headers, timeout=timeout, **kwargs)
        return resp, new_token
    return resp, token


def get_group_id(session: requests.Session, ome_ip: str, token: str, group_name: str) -> int:
    url = f"https://{ome_ip}/api/GroupService/Groups?$top=8000"
    resp, _ = request_with_token(session, 'GET', url, token=token, ome_ip=ome_ip, username=args.ome_username, password=args.ome_password)
    if resp.status_code != 200:
        raise RuntimeError(f"Failed to list groups (HTTP {resp.status_code}): {resp.text}")
    data = resp.json()
    groups = data.get('value') or []
    for g in groups:
        if g.get('Name') == group_name:
            gid = g.get('Id')
            print(f"Found Id {gid} for group '{group_name}'")
            return gid
    raise KeyError(f"Group '{group_name}' not found")


def list_devices(
    session: requests.Session,
    ome_ip: str,
    token: str,
    group_id: Optional[int],
) -> Tuple[List[Dict[str, Any]], str]:
    """Return a list of device dicts with at least Id and Name/DeviceName."""
    if group_id is not None:
        print("Setting job scope to specified group")
        base_url = f"https://{ome_ip}/api/GroupService/Groups({group_id})/Devices?$top=8000"
    else:
        print("Setting job scope to all managed iDRAC systems")
        base_url = f"https://{ome_ip}/redfish/v1/Systems/Members?$top=8000"

    devices: List[Dict[str, Any]] = []
    next_url: Optional[str] = base_url
    current_token = token
    while next_url:
        resp, current_token = request_with_token(session, 'GET', next_url, token=current_token, ome_ip=ome_ip, username=args.ome_username, password=args.ome_password)
        if resp.status_code != 200:
            raise RuntimeError(f"Failed to list devices (HTTP {resp.status_code}): {resp.text}")
        body = resp.json()
        page_items = body.get('value')
        if page_items is None:
            page_items = body.get('Members', [])
        if isinstance(page_items, dict) and 'value' in page_items:
            page_items = page_items['value']
        devices.extend(page_items or [])
        next_url = body.get('@odata.nextLink') or body.get('Members@odata.nextLink')
        if next_url and not next_url.startswith('http'):
            next_url = f"https://{ome_ip}/{next_url.lstrip('/') }"
    return devices, current_token


def submit_racadm_job(session: requests.Session, ome_ip: str, token: str, device_id: int, command: str) -> Tuple[Optional[int], str]:
    job_url = f"https://{ome_ip}/api/JobService/Jobs"
    payload = {
        "JobName": "Remote Command Line",
        "JobDescription": "RACADM CLI",
        "Schedule": "startnow",
        "State": "enabled",
        "Targets": [{"Id": int(device_id), "Data": "", "TargetType": {"Id": 1000, "Name": "DEVICE"}}],
        "Params": [
            {"Key": "CommandTimeout", "Value": "60"},
            {"Key": "operationName", "Value": "REMOTE_RACADM_EXEC"},
            {"Key": "Command", "Value": command},
        ],
        "JobType": {"Name": "DeviceAction_Task", "Internal": False},
    }
    resp, token = request_with_token(session, 'POST', job_url, token=token, ome_ip=ome_ip, username=args.ome_username, password=args.ome_password, data=json.dumps(payload))
    if resp.status_code != 201:
        try:
            err = resp.json()
        except Exception:
            err = resp.text
        return None, token
    try:
        job_id = resp.json().get('Id')
    except Exception:
        job_id = None
    return job_id, token


def poll_job_completion(session: requests.Session, ome_ip: str, token: str, job_id: int, poll_interval: int, max_wait: int) -> Tuple[str, str]:
    """Poll job until a terminal state. Returns (state_code, state_str)."""
    job_url = f"https://{ome_ip}/api/JobService/Jobs({job_id})"
    status_map = {
        2020: "Scheduled",
        2030: "Queued",
        2040: "Starting",
        2050: "Running",
        2060: "Completed",
        2070: "Failed",
        2090: "Warning",
        2080: "New",
        2100: "Aborted",
        2101: "Paused",
        2102: "Stopped",
        2103: "Canceled",
    }
    deadline = time.time() + max_wait
    current_token = token
    while time.time() < deadline:
        resp, current_token = request_with_token(session, 'GET', job_url, token=current_token, ome_ip=ome_ip, username=args.ome_username, password=args.ome_password)
        if resp.status_code == 200:
            body = resp.json()
            last = (body.get('LastRunStatus') or {}).get('Id')
            if isinstance(last, int):
                if last in (2060, 2070, 2090, 2100, 2101, 2102, 2103):
                    return str(last), status_map.get(last, str(last))
        time.sleep(poll_interval)
    return "-1", "Timeout"


def get_job_output(session: requests.Session, ome_ip: str, token: str, job_id: int) -> Tuple[Optional[str], str]:
    url = f"https://{ome_ip}/api/JobService/Jobs({job_id})/ExecutionHistories"
    resp, token = request_with_token(session, 'GET', url, token=token, ome_ip=ome_ip, username=args.ome_username, password=args.ome_password)
    if resp.status_code != 200:
        return None, f"Failed to get execution histories (HTTP {resp.status_code}): {resp.text}"
    hist = resp.json().get('value') or []
    if not hist:
        return None, "No execution history found"
    details_nav = hist[0].get("ExecutionHistoryDetails@odata.navigationLink")
    if not details_nav:
        return None, "No execution details link found"
    details_url = f"https://{ome_ip}/{details_nav}"
    d_resp, _ = request_with_token(session, 'GET', details_url, token=token, ome_ip=ome_ip, username=args.ome_username, password=args.ome_password)
    if d_resp.status_code != 200:
        return None, f"Failed to get execution details (HTTP {d_resp.status_code}): {d_resp.text}"
    vals = d_resp.json().get('value') or []
    if not vals:
        return None, "No execution details found"
    return vals[0].get('Value'), ""


def main() -> int:
    parser = argparse.ArgumentParser(description='Run RACADM against OME-managed systems via JobService')
    parser.add_argument('-c', dest='command', help='RACADM Command', required=True)
    parser.add_argument('-i', dest='ome_ip', help='OpenManage Enterprise IP/Host', required=True)
    parser.add_argument('-u', dest='ome_username', help='OpenManage Enterprise Username', required=True)
    parser.add_argument('-p', dest='ome_password', help='OpenManage Enterprise Password', required=True)
    parser.add_argument('-g', dest='group_name', help='Target Group name', required=False)
    # TLS options
    parser.add_argument('--insecure', action='store_true', help='Disable TLS certificate verification')
    # Polling options
    parser.add_argument('--poll-interval', type=int, default=5, help='Seconds between job status polls (default: 5)')
    parser.add_argument('--max-wait', type=int, default=120, help='Max seconds to wait per job (default: 120)')

    global args
    args = parser.parse_args()

    session = build_session(insecure=args.insecure)

    try:
        token = authenticate(session, args.ome_ip, args.ome_username, args.ome_password)
        print("Authenticated to OpenManage Enterprise")

        group_id: Optional[int] = None
        if args.group_name:
            group_id = get_group_id(session, args.ome_ip, token, args.group_name)

        devices, token = list_devices(session, args.ome_ip, token, group_id)
        if not devices:
            print("No devices found to target.")
            return 1

        total = 0
        successes = 0
        failures = 0

        for dev in devices:
            total += 1
            dev_id = dev.get('Id')
            dev_name = dev.get('Name') or dev.get('DeviceName') or f"Device {dev_id}"
            job_id, token = submit_racadm_job(session, args.ome_ip, token, dev_id, args.command)
            if not job_id:
                print(f"[{dev_name}] Failed to submit job")
                failures += 1
                continue
            print(f"[{dev_name}] RACADM command submitted (job {job_id}). Polling...")
            state_code, state_str = poll_job_completion(session, args.ome_ip, token, job_id, args.poll_interval, args.max_wait)
            if state_str not in ("Completed",):
                print(f"[{dev_name}] Job state: {state_str} (code {state_code})")
            output, err = get_job_output(session, args.ome_ip, token, job_id)
            print("=" * 80)
            if output is not None:
                print(output)
                successes += 1
            else:
                print(f"No output. {err}")
                failures += 1

        print(f"\nSummary: total={total}, success={successes}, failed={failures}")
        return 0 if failures == 0 else 2

    except Exception as e:
        print(f"Error: {e}")
        return 2


if __name__ == '__main__':
    sys.exit(main())