# byte-histogram

This program is designed to show a distribution of the byte values of a file, read as binary.

It can be used to help determine if a file is encrypted.
Statistics and a histogram of the byte distribution are displayed.

A relative standard deviation close to 1.0 indicates the byte values are quite evenly distributed (a property expected of an encrypted file).
By default, log scaling is used, which should show "full bars" for all byte values of an encrypted file.

Change the scaling mode for histogram bars with the --scale option, which accepts the following options:
  - log
  - minmax
  - max

The bar length is currently fixed at 80 columns.
