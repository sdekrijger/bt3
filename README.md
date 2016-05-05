# bt3
Hex Terminal

Typical use-case of Bt3 is debugging embedded projects by connecting to an UART port and chatting directly in HEX by inputting escaped strings like "\x00\x01" and viewing output in a typical hexdump format.

The ASCII mode shows lines of raw ASCII only, there is no terminal emulation.

Bt3 can append an 8-bit modulo or xor sum to each frame. Bt3 can append CR+LF or one of both to each frame.
