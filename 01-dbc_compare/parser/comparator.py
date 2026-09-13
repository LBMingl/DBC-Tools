"""DBC file comparison engine."""


class DBCComparator:
    """Compares two DBC file parse results."""

    def __init__(self):
        self.left_data = None
        self.right_data = None
        self.diff_results = {
            "nodes": {"only_left": [], "only_right": [], "different": []},
            "messages": {"only_left": [], "only_right": [], "different": []},
            "signals": {"only_left": [], "only_right": [], "different": []},
            "table_values": {"only_left": [], "only_right": [], "different": []},
        }

    def load_dbc(self, left_data, right_data):
        """Load parsed DBC data for comparison."""
        self.left_data = left_data
        self.right_data = right_data

    def compare(self):
        """Perform comparison and return results."""
        if not self.left_data or not self.right_data:
            return self.diff_results

        self._compare_nodes()
        self._compare_messages()
        self._compare_signals()
        self._compare_table_values()

        return self.diff_results

    def _compare_nodes(self):
        """Compare nodes between two DBC files."""
        left_nodes = set(self.left_data["nodes"].keys())
        right_nodes = set(self.right_data["nodes"].keys())

        only_left = left_nodes - right_nodes
        only_right = right_nodes - left_nodes
        common = left_nodes & right_nodes

        self.diff_results["nodes"]["only_left"] = sorted(only_left)
        self.diff_results["nodes"]["only_right"] = sorted(only_right)

        for node_name in sorted(common):
            left_node = self.left_data["nodes"][node_name]
            right_node = self.right_data["nodes"][node_name]

            diffs = []
            if left_node.tx_messages != right_node.tx_messages:
                diffs.append("TX messages differ")
            if left_node.rx_messages != right_node.rx_messages:
                diffs.append("RX messages differ")
            if left_node.attributes != right_node.attributes:
                diffs.append("Attributes differ")

            if diffs:
                self.diff_results["nodes"]["different"].append(
                    {"name": node_name, "diffs": diffs}
                )

    def _compare_messages(self):
        """Compare messages between two DBC files."""
        left_msgs = set(self.left_data["messages"].keys())
        right_msgs = set(self.right_data["messages"].keys())

        only_left = left_msgs - right_msgs
        only_right = right_msgs - left_msgs
        common = left_msgs & right_msgs

        self.diff_results["messages"]["only_left"] = sorted(only_left)
        self.diff_results["messages"]["only_right"] = sorted(only_right)

        for msg_name in sorted(common):
            left_msg = self.left_data["messages"][msg_name]
            right_msg = self.right_data["messages"][msg_name]

            diffs = []
            if left_msg.id != right_msg.id:
                diffs.append(f"ID: 0x{left_msg.id:X} vs 0x{right_msg.id:X}")
            if left_msg.dlc != right_msg.dlc:
                diffs.append(f"DLC: {left_msg.dlc} vs {right_msg.dlc}")
            if left_msg.transmitter != right_msg.transmitter:
                diffs.append(
                    f"Transmitter: {left_msg.transmitter} vs {right_msg.transmitter}"
                )

            left_sigs = set(s.name for s in left_msg.signals)
            right_sigs = set(s.name for s in right_msg.signals)
            if left_sigs != right_sigs:
                only_left_sigs = left_sigs - right_sigs
                only_right_sigs = right_sigs - left_sigs
                if only_left_sigs:
                    diffs.append(f"Only left signals: {', '.join(only_left_sigs)}")
                if only_right_sigs:
                    diffs.append(f"Only right signals: {', '.join(only_right_sigs)}")

            if left_msg.attributes != right_msg.attributes:
                diffs.append("Attributes differ")

            if diffs:
                self.diff_results["messages"]["different"].append(
                    {"name": msg_name, "diffs": diffs}
                )

    def _compare_signals(self):
        """Compare signals between two DBC files."""
        left_sigs = set(self.left_data["signals"].keys())
        right_sigs = set(self.right_data["signals"].keys())

        only_left = left_sigs - right_sigs
        only_right = right_sigs - left_sigs
        common = left_sigs & right_sigs

        self.diff_results["signals"]["only_left"] = sorted(only_left)
        self.diff_results["signals"]["only_right"] = sorted(only_right)

        for sig_name in sorted(common):
            left_sig = self.left_data["signals"][sig_name]
            right_sig = self.right_data["signals"][sig_name]

            diffs = []
            if left_sig.start_bit != right_sig.start_bit:
                diffs.append(f"Start bit: {left_sig.start_bit} vs {right_sig.start_bit}")
            if left_sig.length != right_sig.length:
                diffs.append(f"Length: {left_sig.length} vs {right_sig.length}")
            if left_sig.byte_order != right_sig.byte_order:
                diffs.append(
                    f"Byte order: {left_sig.byte_order} vs {right_sig.byte_order}"
                )
            if left_sig.factor != right_sig.factor or left_sig.offset != right_sig.offset:
                diffs.append(
                    f"Factor/Offset: ({left_sig.factor},{left_sig.offset}) vs ({right_sig.factor},{right_sig.offset})"
                )
            if left_sig.unit != right_sig.unit:
                diffs.append(f"Unit: '{left_sig.unit}' vs '{right_sig.unit}'")
            if left_sig.receivers != right_sig.receivers:
                diffs.append("Receivers differ")

            if diffs:
                self.diff_results["signals"]["different"].append(
                    {"name": sig_name, "diffs": diffs}
                )

    def _compare_table_values(self):
        """Compare table values between two DBC files."""
        left_tables = set(self.left_data["table_values"].keys())
        right_tables = set(self.right_data["table_values"].keys())

        only_left = left_tables - right_tables
        only_right = right_tables - left_tables
        common = left_tables & right_tables

        self.diff_results["table_values"]["only_left"] = sorted(only_left)
        self.diff_results["table_values"]["only_right"] = sorted(only_right)

        for table_name in sorted(common):
            left_table = self.left_data["table_values"][table_name]
            right_table = self.right_data["table_values"][table_name]

            if left_table.values != right_table.values:
                self.diff_results["table_values"]["different"].append(
                    {"name": table_name, "diffs": ["Values differ"]}
                )

    def get_summary(self):
        """Get comparison summary."""
        summary = {
            "nodes": {
                "only_left": len(self.diff_results["nodes"]["only_left"]),
                "only_right": len(self.diff_results["nodes"]["only_right"]),
                "different": len(self.diff_results["nodes"]["different"]),
            },
            "messages": {
                "only_left": len(self.diff_results["messages"]["only_left"]),
                "only_right": len(self.diff_results["messages"]["only_right"]),
                "different": len(self.diff_results["messages"]["different"]),
            },
            "signals": {
                "only_left": len(self.diff_results["signals"]["only_left"]),
                "only_right": len(self.diff_results["signals"]["only_right"]),
                "different": len(self.diff_results["signals"]["different"]),
            },
            "table_values": {
                "only_left": len(self.diff_results["table_values"]["only_left"]),
                "only_right": len(self.diff_results["table_values"]["only_right"]),
                "different": len(self.diff_results["table_values"]["different"]),
            },
        }
        return summary
