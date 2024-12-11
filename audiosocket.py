import socket
from threading import Thread
from time import sleep

class Audiosocket:
    def __init__(self, bind_info, timeout=None):

        # By default, features of audioop (for example: resampling
        # or remixing input/output) are disabled
        self.user_resample = None
        self.asterisk_resample = None

        if not isinstance(bind_info, tuple):
            raise TypeError(
                "Expected tuple (addr, port), received", type(bind_info))

        self.addr, self.port = bind_info

        self.initial_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.initial_sock.bind((self.addr, self.port))
        self.initial_sock.settimeout(timeout)
        self.initial_sock.listen(5)  # Allows up to 5 pending connections

        # If the user didn't specify a port, the one that the operating system
        # chose is available in this attribute
        self.port = self.initial_sock.getsockname()[1]

    # Optionally prepares audio sent by the user to
    # the specifications needed by audiosocket (16-bit, 8KHz mono LE PCM).
    # Audio sent in must be in PCM or ULAW format

    def prepare_input(self, inrate=44000, channels=2, ulaw2lin=False):
        self.user_resample = audioop_struct(
            rate=inrate,
            channels=channels,
            ulaw2lin=ulaw2lin,
            ratecv_state=None,
        )

    def get_uuid(self):
        data_types = types_struct()
        return data_types.uuid

    # Optionally prepares audio sent by audiosocket to
    # the specifications of the user
    def prepare_output(self, outrate=44000, channels=2, ulaw2lin=False):
        self.asterisk_resample = audioop_struct(
            rate=outrate,
            channels=channels,
            ulaw2lin=ulaw2lin,
            ratecv_state=None,
        )

    def listen(self):
        print('Listening on', self.addr, self.port)

        def handle_connection(conn, peer_addr):
            connection = Connection(
                conn,
                peer_addr,
                self.user_resample,
                self.asterisk_resample,
            )
            connection._process()

        while True:
            try:
                conn, peer_addr = self.initial_sock.accept()
                print(f"Accepted connection from {peer_addr}")
                connection_thread = Thread(target=handle_connection, args=(conn, peer_addr))
                connection_thread.start()
                sleep(0.1)
            except socket.timeout:
                continue
            except Exception as e:
                print(f"Error accepting connection: {e}")

        # *** If we want this single object to serve multiple simultaneous connections, accept() will have to be put in a while loop
        # If this does become the case, what is the best way to deliver the queue objects to the caller, keep them wrapped in read/write methods?
