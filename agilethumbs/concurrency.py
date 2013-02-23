"""
Provides a context manager for dealing with concurrency shennanigans.

Quite possibly overkill, but the idea is to avoid overlapping requests for the
same image generating that image multiple times. Nothing would actually break
in this scenario but it would be possible to do quite a lot of unnecessary work.
"""
import os
import errno
import fcntl
from contextlib import contextmanager

@contextmanager
def atomic_create(filename, mode=0600, makedirs=True):
	"""
	Atomically, and exclusively, create a file.
	
	Returns either a file object to write to or None if the file already exists.
	
	If the file doesn't yet exist but is in the process of being created (i.e.,
	if some other process has called atomic_create on that location) then the
	manager blocks until the other process has finished before returning None.
	
	Output is written to a temporary location until the context manager exits,
	at which point the file is moved into the target location, providing
	atomicity.
	"""
	if makedirs:
		directory = os.path.dirname(filename)
		try:
			os.makedirs(directory)
		except OSError as e:
			if e.errno != errno.EEXIST:
				raise
	
	lock_path = '%s.lock' % filename
	fileobj = open(lock_path, 'a+b', 0600)
	try:
		# Try to acquire exclusive lock without blocking
		fcntl.lockf(fileobj.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
	except IOError as e:
		if e.errno != errno.EAGAIN:
			raise
		# Someone else has already got a lock. Block until we can acquire a
		# shared lock (i.e., until the other process has finished)
		fcntl.lockf(fileobj.fileno(), fcntl.LOCK_SH)
		# Release the lock and close the lock file (no need to remove the file;
		# whoever had the exclusive lock on it is responsible for that)
		fcntl.lockf(fileobj.fileno(), fcntl.LOCK_UN)
		fileobj.close()
		# Yield None to indicate that the file now exists
		yield None
		# And we're done
		return
	
	moved = False
	try:
		if os.path.exists(filename):
			yield None
		else:
			# Yield file handle, actual content creation happens here
			yield fileobj
			# Move it into place
			os.chmod(lock_path, mode)
			os.rename(lock_path, filename)
			moved = True
	finally:
		# Clean up
		fcntl.lockf(fileobj.fileno(), fcntl.LOCK_UN)
		fileobj.close()
		if not moved:
			os.unlink(lock_path)
