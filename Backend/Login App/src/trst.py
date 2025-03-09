def consolidate_permissions(permission_list):
    hierarchy = {
        "Self": 1,
        "Group": 2,
        "Users": 3,
        "All": 4
    }
    
    permission_map = {}

    for perm in permission_list:
        parts = perm.split(": ")
        if len(parts) == 2:
            category, level = parts
            level = level.strip()
            
            # Ensure the category has a set to store all relevant scopes
            if category not in permission_map:
                permission_map[category] = set()
            
            permission_map[category].add(level)

    # Consolidate permissions while keeping multiple scopes if necessary
    consolidated_permissions = []
    for category, levels in permission_map.items():
        if "All" in levels:  
            # "All" overrides everything else, so just keep it
            consolidated_permissions.append(f"{category}: All")
        else:
            # Keep multiple scopes (e.g., both "Group" and "Users" if present)
            sorted_levels = sorted(levels, key=lambda lvl: hierarchy[lvl])  # Sort by hierarchy
            consolidated_permissions.append(f"{category}: {', '.join(sorted_levels)}")

    return consolidated_permissions

input_permissions = [
    "FaceGuard Read: Self",
    "FaceGuard Read: Group",
    "FaceGuard Read: Users",
    "FaceGuard Create: Self",
    "FaceGuard Create: Group"
]

output = consolidate_permissions(input_permissions)
print(output)