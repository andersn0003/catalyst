import pytest

from brownie import convert, ZERO_ADDRESS


def evmBytes32ToAddress(bytes32):
    return convert.to_address(bytes32[12:])


# Decode a Catalyst message in Python with Brownie.
@pytest.fixture(scope="session")
def decodePayload():
    def _decodePayload(data, decode_address=evmBytes32ToAddress):
        context = data[0]
        if context & 1:
            return {
                "_context": data[0],
                "_fromPool": decode_address(data[1:33]),
                "_toPool": decode_address(data[33:65]),
                "_who": decode_address(data[65:97]),
                "_LU": convert.to_uint(data[97:129]),
                "_minOut": convert.to_uint(data[129:161]),
                "_escrowAmount": convert.to_uint(data[161:193])
            }
        customDataLength = convert.to_uint(data[226:228], type_str="uint16")
        return {
            "_context": data[0],
            "_fromPool": decode_address(data[1:33]),
            "_toPool": decode_address(data[33:65]),
            "_who": decode_address(data[65:97]),
            "_U": convert.to_uint(data[97:129]),
            "_assetIndex": convert.to_uint(data[129], type_str="uint8"),
            "_minOut": convert.to_uint(data[130:162]),
            "_escrowAmount": convert.to_uint(data[162:194]),
            "_escrowToken": decode_address(data[194:226]),
            "customDataLength": customDataLength,
            "_customDataTarget": decode_address(data[228:260]) if customDataLength > 0 else None,
            "_customData": data[260:260+customDataLength - 32] if customDataLength > 0 else None
        }
    
    yield _decodePayload


# Construct a Catalyst message in Python with Brownie.
@pytest.fixture(scope="session")
def payloadConstructor():
    def _payloadConstructor(
    _from,
    _to,
    _who,
    _U,
    _assetIndex=0,
    _minOut=0,
    _escrowAmount=0,
    _escrowToken=ZERO_ADDRESS,
    _context=convert.to_bytes(0, type_str="bytes1"),
):
        return (
            _context
            + convert.to_bytes(_from, type_str="bytes32")
            + convert.to_bytes(_to, type_str="bytes32")
            + _who
            + convert.to_bytes(_U, type_str="bytes32")
            + convert.to_bytes(_assetIndex, type_str="bytes1")
            + convert.to_bytes(_minOut, type_str="bytes32")
            + convert.to_bytes(_escrowAmount, type_str="bytes32")
            + convert.to_bytes(_escrowToken, type_str="bytes32")
            + convert.to_bytes(0, type_str="bytes2")
        )  
    
    yield _payloadConstructor
    

# Construct a Catalyst message in Python with Brownie.
@pytest.fixture(scope="session")
def LiquidityPayloadConstructor():
    def _liquidityPayloadConstructor(
        _from,
        _to,
        _who,
        _U,
        _minOut=0,
        _escrowAmount=0,
        _context=convert.to_bytes(1, type_str="bytes1")
    ):
        return (
            _context
            + convert.to_bytes(_from, type_str="bytes32")
            + convert.to_bytes(_to, type_str="bytes32")
            + _who
            + convert.to_bytes(_U, type_str="bytes32")
            + convert.to_bytes(_minOut, type_str="bytes32")
            + convert.to_bytes(_escrowAmount, type_str="bytes32")
            + convert.to_bytes(0, type_str="bytes2")
    )
    
    yield LiquidityPayloadConstructor


@pytest.fixture(scope="session")
def relative_error():
    def _relative_error(a, b):
        if a is None or b is None:
            return None
        
        if a == 0 and b == 0:
            return 0

        return 2*(a - b)/(abs(a) + abs(b))

    yield _relative_error


def assert_relative_error(relative_error):
    def _assert_relative_error(a, b, low_error_bound, high_error_bound=None, error_id=None):
        if high_error_bound is None:
            high_error_bound = low_error_bound
        
        error = relative_error(a, b)
        
        error_id_string = f"(ERR: {error_id})" if error_id is not None else ""
        assert low_error_bound <= error <= high_error_bound, f"Error {error} is outside allowed range [{low_error_bound}, {high_error_bound}] {error_id_string}"

    yield _assert_relative_error