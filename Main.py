from application.server.Server import Server

CSV_PATH = "resources/cameras.csv"

"""
Multi Connection Server (MCS)

Server application software developed for
Panasonic Marketing Europe GmbH

Author: Phillip Mai & Dorian Paeth
Copyright: Copyright 2020, Multi Connection Server
Credits: Phillip Mai, Dorian Paeth, Marco Schulz, 
         Panasonic Marketing Europe GmbH
License: Trade secret
Version: 1.0.0
Maintainer: Panasonic Marketing Europe GmbH
Email: phillip.mai@live.de & mail@dorianpaeth.de
Status: Release v1.0.0

"""

if __name__ == '__main__':
    """
    # Main Class #

    Main class to start the server application - Multi Connection Server (MCS).
    Use the CSV_PATH csv data to configure all cameras etc.
    For support write an Email to phillip.mai@live.de || mail@dorianpaeth.de.
    """
    server = Server(CSV_PATH)
    server.start()
