def parse_storage_quota(quota_str):
    """
    Parses storage quota string with unit suffix into Gigabytes (GB).
    Hardened against invalid types, empty values, and malformed strings.
    """
    if not isinstance(quota_str, str) or not quota_str.strip():
        raise ValueError("Invalid quota input: must be a non-empty string.")
    
    cleaned = quota_str.strip().upper()
    if len(cleaned) < 3:
        raise ValueError("Invalid quota format: too short.")
        
    val_str = cleaned[:-2]
    unit = cleaned[-2:]
    
    try:
        value = int(val_str)
    except ValueError:
        raise ValueError(f"Invalid numeric value in quota: {val_str}")
        
    multipliers = {
        "MB": 0.001,
        "GB": 1.0,
        "TB": 1000.0
    }
    
    if unit not in multipliers:
        raise KeyError(f"Unknown storage unit: {unit}")
        
    gb_total = value * multipliers[unit]
    return f"Quota: {gb_total:.2f} GB"

def compute_compression_ratio(size_metric_str):
    """
    Computes compression ratio: raw_bytes / compressed_bytes.
    Hardened against missing colons, non-numeric values, and zero division.
    """
    if not isinstance(size_metric_str, str) or ':' not in size_metric_str:
        raise ValueError("Invalid compression format: expected 'raw:compressed'.")
        
    parts = size_metric_str.split(':')
    if len(parts) != 2:
        raise ValueError("Invalid compression format: multiple colons found.")
        
    raw_str, comp_str = parts
    
    try:
        raw_bytes = float(raw_str)
        comp_bytes = float(comp_str)
    except ValueError:
        raise ValueError("Non-numeric bytes provided.")
        
    if comp_bytes == 0:
        raise ZeroDivisionError("Compressed bytes cannot be zero.")
        
    ratio = raw_bytes / comp_bytes
    return round(ratio, 2)

def lookup_bandwidth_tier_rate(tier_descriptor):
    """
    Looks up rate per GB for egress traffic using the first 3 letters of the tier name.
    Hardened against invalid descriptors or empty values.
    """
    if not isinstance(tier_descriptor, str) or not tier_descriptor.strip():
        raise ValueError("Invalid tier descriptor: must be a non-empty string.")
        
    prefix = tier_descriptor.strip().upper()[:3]
    tier_rates = {
        "HOT": 0.08,
        "COL": 0.05,
        "ARC": 0.02
    }
    
    if prefix not in tier_rates:
        raise KeyError(f"Unknown tier prefix: {prefix}")
        
    return tier_rates[prefix]

def main():
    print("==== Running parse_storage_quota ====")
    q_input = input("Enter quota (e.g. 500MB, 10GB, 2TB): ")
    try:
        print(parse_storage_quota(q_input))
    except Exception as e:
        print("Error:", e)

    print("\n==== Running compute_compression_ratio ====")
    c_input = input("Enter raw:compressed bytes (e.g. 1024:256): ")
    try:
        print("Compression Ratio:", compute_compression_ratio(c_input))
    except Exception as e:
        print("Error:", e)

    print("\n==== Running lookup_bandwidth_tier_rate ====")
    t_input = input("Enter tier descriptor (e.g. HOT_TIER, COLD, ARCHIVE): ")
    try:
        print("Rate per GB: $", lookup_bandwidth_tier_rate(t_input))
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    main()