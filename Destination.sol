// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "./BridgeToken.sol";

contract Destination is AccessControl {
    bytes32 public constant WARDEN_ROLE = keccak256("BRIDGE_WARDEN_ROLE");
    bytes32 public constant CREATOR_ROLE = keccak256("CREATOR_ROLE");
	mapping( address => address) public underlying_tokens;
	mapping( address => address) public wrapped_tokens;
	address[] public tokens;

	event Creation( address indexed underlying_token, address indexed wrapped_token );
	event Wrap( address indexed underlying_token, address indexed wrapped_token, address indexed to, uint256 amount );
	event Unwrap( address indexed underlying_token, address indexed wrapped_token, address frm, address indexed to, uint256 amount );

    constructor( address admin ) {
        _grantRole(DEFAULT_ADMIN_ROLE, admin);
        _grantRole(CREATOR_ROLE, admin);
        _grantRole(WARDEN_ROLE, admin);
    }

	function wrap(address _underlying_token, address _recipient, uint256 _amount ) 
		public onlyRole(WARDEN_ROLE) {
		//YOUR CODE HERE

		require(_recipient != address(0), "Recipient cannot be zero");
		address wrapped_addr = underlying_tokens[_underlying_token];
		require(wrapped_addr != address(0), "Token not registered");

		BridgeToken wrapped = BridgeToken(wrapped_addr);
		wrapped.mint(_recipient, _amount);
	}

	function unwrap(address _wrapped_token, address _recipient, uint256 _amount ) public {
		//YOUR CODE HERE
		require(_recipent != address(0), "Recipient cannot be zero");
		address underlying_addr = wrapped_tokens[_wrapped_token];
		require(underlying_addr != address(0), "Wrapped token not registerd");

		BridgeToken wrapped = BridgeToken(_wrapped_token);

		// only sender should be allowed to burn their own tokens
		require(wrapped.balanceOf(msg.sender) >= _amount, "Insufficient balance");
		wrapped.burnFrom(msg.sender, _amount);

		emit Unwrap(underlying_addr, _wrapped_token, msg.sender, _recipient, _amount);
	}

	function createToken(address _underlying_token, string memory name, string memory symbol 
		) public onlyRole(CREATOR_ROLE) returns(address) {
		//YOUR CODE HERE
		require(
			_underlying_token != address(0),
			"Underlying token cannot be zero address"
		);
		require(
			underying_tokens[_underlying_token] == address(0),
			"Token already registered"
		);

		// deploy new BridgeToken
		BridgeToken wrapped = new BridgeToken(
			_underlying_token,
			name,
			symbol,
			address(this)
		);

		// update mappings
		underlying_tokens[_underlying_token] = address(wrapped);
		wrapped_tokens[address(wrapped)) = _underlying_token;
		tokens.push(address(wrapped));

		emit Creation(_underlying_token, address(wrapped));
		return address(wrapped);
		
	}

}
