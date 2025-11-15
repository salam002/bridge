// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";

contract Source is AccessControl {
    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");
    bytes32 public constant WARDEN_ROLE = keccak256("BRIDGE_WARDEN_ROLE");
	mapping( address => bool) public approved;
	address[] public tokens;

	event Deposit( address indexed token, address indexed recipient, uint256 amount );
	event Withdrawal( address indexed token, address indexed recipient, uint256 amount );
	event Registration( address indexed token );

    constructor( address admin ) {
        _grantRole(DEFAULT_ADMIN_ROLE, admin);
        _grantRole(ADMIN_ROLE, admin);
        _grantRole(WARDEN_ROLE, admin);

    }

	function deposit(address _token, address _recipient, uint256 _amount ) public {
		//YOUR CODE HERE

        require(approved[_token], "Token registed");

        // Use the ERC20 “transferFrom” function to pull the tokens into the deposit contract
        bool succ = IERC20(_token).transferFrom(msg.sender, address(this), _amount);
        require(succ, "Transfer unsuccessful");

        emit Deposit(_token, _recipient, _amount);


	}

	function withdraw(address _token, address _recipient, uint256 _amount ) onlyRole(WARDEN_ROLE) public {
		//YOUR CODE HERE

        /*
        Check that the function is being called by the contract owner
        Push the tokens to the recipient using the ERC20 “transfer” function
        Emit a “Withdraw” event
        */

        bool succ = IERC20(_token).transfer(_recipient, _amount);
        require(succ, "Withdrawal failed");

        emit Withdrawal(_token, _recipient, _amount);
    }


	function registerToken(address _token) onlyRole(ADMIN_ROLE) public {
		//YOUR CODE HERE

        /*
        Check that the function is being called by the contract owner
        Check that the token has not already been registered
        Add the token address to the list of registered tokens
        Emit a Registration event
        */


        require(!approved[_token], "Token already registed");

        approved[_token] = true;

        emit Registration(_token);
	}


}


