# Proto Python

This is a coding exercise in parsing a fixed length encoded file using Python.
The records are dummy financial transaction records with no relation to real world customers or accounts.

This application is required to interface with an old-school mainframe format that we've named "MPS7".
This means consuming a proprietary binary protocol format specification.

## Task

This application will read in a transaction log, `txnlog.dat`, and parse it according to the specification in Notes below.

It will answer the following questions:

* What is the total amount in dollars of debits?
* What is the total amount in dollars of credits?
* How many autopays were started?
* How many autopays were ended?
* What is balance of user ID 2456938384156277127?

The complete instructions for compiling and running is in an included COMMENTS file.

## Notes

Because `txnlog.dat` is a binary file, it can't be read by a normal text editor like sublime or vim.
Instead, it must be read programatically and parsed for the data needed.

This is how the transaction log is structured:

Header:

| 4 byte magic string "MPS7" | 1 byte version | 4 byte (uint32) # of records |

The header contains the canonical information about how the records should be processed.
Note: there are fewer than 100 records in `txnlog.dat`.

Record:

| 1 byte record type enum | 4 byte (uint32) Unix timestamp | 8 byte (uint64) user ID |

Record type enum:

* 0x00: Debit
* 0x01: Credit
* 0x02: StartAutopay
* 0x03: EndAutopay

For Debit and Credit record types, there is an additional field, an 8 byte
(float64) amount in dollars, at the end of the record.

All multi-byte fields are encoded in network byte order.

The first record in the file, when fully parsed, will look something like this:

| Record type | Unix timestamp | user ID             | amount in dollars |
|-------------|----------------|---------------------|-------------------|
| 'Debit'     | 1393108945     | 4136353673894269217 | 604.274335557087  |


## Getting Started

Clone this repository locally.
Install required packages via PIP python commands.
Run the program using Python.

### Prerequisites

Environment Requirements:

```
Python v3.7.2 32-bit was used for development of this module

Python Packages Used:
numpy
struct
pandas
datetime
tabulate
```

## Running the tests

Execute Command for test_proto.py:
python test_proto.py

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/your/project/tags). 

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

