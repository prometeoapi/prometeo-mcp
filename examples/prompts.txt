# Example prompts

Using Sandbox sample data.

> To get access in production contact: ventas@prometeoapi.com

## Bank Account Data extraction

"""
With this creds login in prometeo credentials

- provider: "test"
- username: "12345"
- password: "gfdsa"

Then list accounts and retrieve movements from today
"""

## Bank Account Data extraction (OTP interation)

"""
With this creds login in prometeo credentials

- provider: "test"
- username: "12345otp"
- password: "asdfg"

Then list accounts and retrieve movements from today.

If the account asks for a token OTP, pause data extraction until I send the OTP Token.
"""

## Account Validation

"""
Validate the following accounts:
 - MX (999000000000000001)
 - PE (99900000000000000030)
 - BR (BR7299999999010100000001001C1, 58.547.642/0001-95)
"""

## Validate CURP

"""
Validate this CURP (ABCD880304HDWXYZ45)
"""

## Validate CURP

"""
Do a reverse query for CURP

Name: Juan Pérez González
Gender: Male
Date of Birth: 04/03/1986
State: DF
"""
