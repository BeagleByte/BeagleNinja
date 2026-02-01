#!/bin/bash
# append bridges from Bridges/bridges.txt to multiple torrc files
# Path to bridge list file
BRIDGE_FILE="Bridges/bridges.txt"

# Torrc files
TORRC_FILES=("config/torrc1" "config/torrc2" "config/torrc3" "config/torrc4")

# Function to update bridges in a torrc file
update_bridges() {
    local torrc_file=$1

    # Remove old bridge lines
    sed -i '/^Bridge /d' "$torrc_file"
    sed -i '/^UseBridges /d' "$torrc_file"
    sed -i '/^ClientTransportPlugin /d' "$torrc_file"

    # Add UseBridges
    echo "UseBridges 1" >> "$torrc_file"

    # Add ClientTransportPlugin for obfs4
    echo "ClientTransportPlugin obfs4 exec /usr/bin/obfs4proxy" >> "$torrc_file"

    # Read and add each bridge from file
    while IFS= read -r line || [ -n "$line" ]; do
        # Skip empty lines and comments
        [[ -z "$line" || "$line" =~ ^[[:space:]]*# ]] && continue

        # Add Bridge prefix if not present
        if [[ "$line" =~ ^Bridge ]]; then
            echo "$line" >> "$torrc_file"
        else
            echo "Bridge $line" >> "$torrc_file"
        fi
    done < "$BRIDGE_FILE"

    echo "Updated $torrc_file"
}

# Check if bridge file exists
if [ ! -f "$BRIDGE_FILE" ]; then
    echo "Error: Bridge file '$BRIDGE_FILE' not found"
    exit 1
fi

# Update all torrc files
for torrc in "${TORRC_FILES[@]}"; do
    if [ -f "$torrc" ]; then
        update_bridges "$torrc"
    else
        echo "Warning: $torrc not found"
    fi
done

echo "All torrc files updated with bridges from $BRIDGE_FILE"


