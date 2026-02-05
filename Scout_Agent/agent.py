from ce_client import CostExplorerClient
from parser import parse_cost_response
from detector import detect_spikes
import config as config

def run():
    ce = CostExplorerClient()

    curr_raw = ce.get_cost_by_service_region(*config.CURRENT_WINDOW)
    prev_raw = ce.get_cost_by_service_region(*config.PREVIOUS_WINDOW)

    curr = parse_cost_response(curr_raw)
    prev = parse_cost_response(prev_raw)

    return detect_spikes(
        curr,
        prev,
        config.PCT_THRESHOLD,
        config.ABS_THRESHOLD
    )
