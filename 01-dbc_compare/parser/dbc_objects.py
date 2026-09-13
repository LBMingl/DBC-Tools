"""DBC data structures."""


class NodeDBC:
    """Represents a CAN node/ECU."""

    def __init__(self, name):
        self.name = name
        self.tx_messages = set()
        self.rx_messages = set()
        self.attributes = {}

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        if isinstance(other, NodeDBC):
            return self.name == other.name
        return False

    def __repr__(self):
        return f"NodeDBC({self.name})"


class SignalDBC:
    """Represents a CAN signal."""

    def __init__(self, name):
        self.name = name
        self.start_bit = 0
        self.length = 0
        self.byte_order = "Little Endian"
        self.value_type = "Unsigned"
        self.factor = 1
        self.offset = 0
        self.min_value = 0
        self.max_value = 0
        self.unit = ""
        self.receivers = set()
        self.values = {}
        self.attributes = {}
        self.mux_value = None
        self.mux_indicator = ""

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        if isinstance(other, SignalDBC):
            return self.name == other.name
        return False

    def __repr__(self):
        return f"SignalDBC({self.name})"


class MessageDBC:
    """Represents a CAN message."""

    def __init__(self, name, id_, dlc):
        self.name = name
        self.id = id_
        self.dlc = dlc
        self.transmitter = ""
        self.signals = []
        self.attributes = {}
        self.comment = ""

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        if isinstance(other, MessageDBC):
            return self.name == other.name
        return False

    def __repr__(self):
        return f"MessageDBC({self.name}, ID=0x{self.id:X})"


class TableValDBC:
    """Represents a table value definition."""

    def __init__(self, name):
        self.name = name
        self.values = {}
        self.descriptions = {}

    def set_value(self, value, description):
        self.values[value] = description
        self.descriptions[value] = description

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        if isinstance(other, TableValDBC):
            return self.name == other.name
        return False


class SynSigType:
    """Synopsis signal type for display."""

    def __init__(self):
        self.tx_node = ""
        self.rx_node = ""


class SynMesType:
    """Synopsis message type for display."""

    def __init__(self):
        self.signal_structure = ""
        self.address = 0
