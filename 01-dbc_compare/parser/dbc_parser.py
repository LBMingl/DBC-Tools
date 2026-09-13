"""DBC file parser implementation."""

import re
from .dbc_objects import NodeDBC, MessageDBC, SignalDBC, TableValDBC


class DBCParser:
    """Parser for DBC (CAN database) files."""

    def __init__(self):
        self.nodes = {}
        self.messages = {}
        self.signals = {}
        self.table_values = {}
        self.attributes = {}
        self.attribute_defaults = {}
        self.comments = {}

    def parse_file(self, file_path):
        """Parse a DBC file and populate data structures."""
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()

        current_message = None
        current_signal = None

        for line in lines:
            stripped = line.strip()
            if not stripped or stripped.startswith("//"):
                continue

            if stripped.startswith("BU_:"):
                self._parse_nodes(stripped)
            elif stripped.startswith("BO_"):
                current_message = self._parse_message(stripped)
                current_signal = None
            elif stripped.startswith("SG_"):
                if current_message:
                    current_signal = self._parse_signal(stripped, current_message)
            elif stripped.startswith("BA_DEF_"):
                self._parse_attribute_def(stripped)
            elif stripped.startswith("BA_DEF_DEF_"):
                self._parse_attribute_default(stripped)
            elif stripped.startswith("BA_"):
                self._parse_attribute(stripped)
            elif stripped.startswith("VAL_"):
                self._parse_table_value(stripped)
            elif stripped.startswith("CM_"):
                self._parse_comment(stripped)

        return {
            "nodes": self.nodes,
            "messages": self.messages,
            "signals": self.signals,
            "table_values": self.table_values,
            "attributes": self.attributes,
            "attribute_defaults": self.attribute_defaults,
            "comments": self.comments,
        }

    def _parse_nodes(self, line):
        """Parse node definitions."""
        match = re.match(r"BU_:\s*(.*)", line)
        if match:
            node_names = match.group(1).strip().split()
            for name in node_names:
                if name and name != ":":
                    self.nodes[name] = NodeDBC(name)

    def _parse_message(self, line):
        """Parse message definition."""
        match = re.match(r"BO_\s+(\d+)\s+(\w+)\s*:\s*(\d+)\s+(\w+)", line)
        if match:
            msg_id = int(match.group(1))
            msg_name = match.group(2)
            dlc = int(match.group(3))
            transmitter = match.group(4)

            message = MessageDBC(msg_name, msg_id, dlc)
            message.transmitter = transmitter
            self.messages[msg_name] = message

            if transmitter in self.nodes:
                self.nodes[transmitter].tx_messages.add(msg_name)

            return message
        return None

    def _parse_signal(self, line, message):
        """Parse signal definition."""
        match = re.match(
            r"SG_\s+(\w+)(\w*)\s*:\s*(\d+)\|(\d+)@(\d+)([+-])\s*\(([0-9.eE+-]+),([0-9.eE+-]+)\)\s*\[([0-9.eE+-]+)\|([0-9.eE+-]+)\]\s*\"([^\"]*)\"\s*(.*)",
            line,
        )
        if match:
            sig_name = match.group(1)
            mux_indicator = match.group(2)
            start_bit = int(match.group(3))
            length = int(match.group(4))
            byte_order = int(match.group(5))
            value_type = match.group(6)
            factor = float(match.group(7))
            offset = float(match.group(8))
            min_val = float(match.group(9))
            max_val = float(match.group(10))
            unit = match.group(11)
            receivers = match.group(12).strip().split(",")

            signal = SignalDBC(sig_name)
            signal.start_bit = start_bit
            signal.length = length
            signal.byte_order = "Little Endian" if byte_order == 1 else "Big Endian"
            signal.value_type = "Signed" if value_type == "-" else "Unsigned"
            signal.factor = factor
            signal.offset = offset
            signal.min_value = min_val
            signal.max_value = max_val
            signal.unit = unit
            signal.mux_indicator = mux_indicator

            for receiver in receivers:
                receiver = receiver.strip()
                if receiver and receiver != "Vector__XXX":
                    signal.receivers.add(receiver)
                    if receiver in self.nodes:
                        self.nodes[receiver].rx_messages.add(message.name)

            message.signals.append(signal)
            self.signals[sig_name] = signal

            return signal
        return None

    def _parse_attribute_def(self, line):
        """Parse attribute definition."""
        match = re.match(r'BA_DEF_\s+(?:(BO_|BU_|SG_)\s+)?"([^"]+)"\s+(.*)', line)
        if match:
            obj_type = match.group(1) or ""
            attr_name = match.group(2)
            attr_type = match.group(3).strip()
            self.attributes[attr_name] = {"type": obj_type, "value_type": attr_type}

    def _parse_attribute_default(self, line):
        """Parse attribute default value."""
        match = re.match(r'BA_DEF_DEF_\s+"([^"]+)"\s+(.*)', line)
        if match:
            attr_name = match.group(1)
            default_val = match.group(2).strip().strip('"')
            self.attribute_defaults[attr_name] = default_val

    def _parse_attribute(self, line):
        """Parse attribute value assignment."""
        match = re.match(r'BA_\s+"([^"]+)"\s+(.*)', line)
        if match:
            attr_name = match.group(1)
            rest = match.group(2).strip()

            if rest.startswith("BU_"):
                node_match = re.match(r'BU_\s+"?(\w+)"?\s+"?([^"]*)"?', rest)
                if node_match:
                    node_name = node_match.group(1)
                    value = node_match.group(2)
                    if node_name in self.nodes:
                        self.nodes[node_name].attributes[attr_name] = value
            elif rest.startswith("BO_"):
                msg_match = re.match(r'BO_\s+(\d+)\s+"?([^"]*)"?', rest)
                if msg_match:
                    msg_id = int(msg_match.group(1))
                    value = msg_match.group(2)
                    for msg in self.messages.values():
                        if msg.id == msg_id:
                            msg.attributes[attr_name] = value
                            break
            elif rest.startswith("SG_"):
                sig_match = re.match(r'SG_\s+(\d+)\s+(\w+)\s+"?([^"]*)"?', rest)
                if sig_match:
                    msg_id = int(sig_match.group(1))
                    sig_name = sig_match.group(2)
                    value = sig_match.group(3)
                    for msg in self.messages.values():
                        if msg.id == msg_id:
                            for sig in msg.signals:
                                if sig.name == sig_name:
                                    sig.attributes[attr_name] = value
                                    break

    def _parse_table_value(self, line):
        """Parse table value definitions."""
        match = re.match(r'VAL_\s+(\d+)\s+(\w+)\s+(.*?);', line)
        if match:
            msg_id = int(match.group(1))
            sig_name = match.group(2)
            values_str = match.group(3)

            table = TableValDBC(f"{msg_id}_{sig_name}")

            val_matches = re.findall(r'(\d+)\s+"([^"]*)"', values_str)
            for val, desc in val_matches:
                table.set_value(int(val), desc)

            self.table_values[f"{msg_id}_{sig_name}"] = table

    def _parse_comment(self, line):
        """Parse comments."""
        match = re.match(r'CM_\s+(.*)', line)
        if match:
            rest = match.group(1).strip()
            if rest.startswith('"'):
                comment = rest.strip('"').rstrip(";").strip()
                self.comments["network"] = comment
            else:
                obj_match = re.match(r'(BU_|BO_|SG_)\s+"?(\w+)"?\s+"([^"]*)";?', rest)
                if obj_match:
                    obj_type = obj_match.group(1)
                    obj_name = obj_match.group(2)
                    comment = obj_match.group(3)
                    self.comments[f"{obj_type}_{obj_name}"] = comment

    def clear(self):
        """Clear all parsed data."""
        self.nodes.clear()
        self.messages.clear()
        self.signals.clear()
        self.table_values.clear()
        self.attributes.clear()
        self.attribute_defaults.clear()
        self.comments.clear()
