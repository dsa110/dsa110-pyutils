from psrdada import Reader
import h5py
import numpy as np
import sysv_ipc
import struct


def unpack_message(dat):
	"""
	Takes candidate metadata sent via System V IPC message queue from 
	heimdall and decodes it to be used in python.
	"""

	first_idx = struct.unpack('Q', dat[0][:8])[0]
	snr = struct.unpack('f', dat[0][8:12])[0]
	samp_idx = struct.unpack('Q', dat[0][12:20])[0]
	time_since = struct.unpack('f', dat[0][20:24])[0]
	h_group_filter_inds = struct.unpack('Q', dat[0][24:32])[0]
	h_group_dm_inds = struct.unpack('Q', dat[0][32:40])[0]
	h_group_dms = struct.unpack('f', dat[0][40:44])[0]
	h_group_members = struct.unpack('Q', dat[0][44:52])[0]
	MJD = "%0.30f" % np.frombuffer(dat[0][52:68], dtype=np.float128)[0]
	MJD = np.string_(MJD)
	cand_MJD = struct.unpack('i', dat[0][68:72])[0]
	cand_hour = struct.unpack('i', dat[0][72:76])[0]
	cand_minute = struct.unpack('i', dat[0][76:80])[0]
	cand_sec = "%0.30f" % np.frombuffer(dat[0][80:96], dtype=np.float128)[0]
	cand_sec = np.string_(cand_sec)
	metadata = np.array(
		[first_idx, snr, samp_idx, time_since, h_group_filter_inds, h_group_dm_inds, h_group_dms,
		 h_group_members, MJD, cand_MJD, cand_hour, cand_minute, cand_sec])
	metadata[-1] = np.string_(metadata[-1])
	metadata[-5] = np.string_(metadata[-5])
	return metadata


def read_buffer(reader):
	"""
	Reads a heimdall buffer as unsigned shorts and returns the dynamic spectrum
	"""
	page = reader.getNextPage()
	data = np.asarray(page)
	reader.markCleared()
	data.dtype = np.uint16
	dy = data.reshape(200000, 2048).T
	return dy


def disp_delay(DM, dt, ftop, fbottom):
	"""
	Calculates the dispersion delay for a given DM in pc/cm^3 and 
	frequencies in GHz
	"""
	return 0.00415 / dt * DM * (fbottom ** -2 - ftop ** -2)


key = sysv_ipc.ftok("/home/user/linux_64/heimdall_buffer/progfile",
					65)  # key of message queue to listen to
queue = sysv_ipc.MessageQueue(key)  # creates message queue
for i in range(queue.current_messages):  # clears any lingering messages in the queue
	queue.receive()
reader = Reader(0xfada)  # defines a psrdada ring buffer to read
count = 0
n_candidates_remaining = 0
dt = 6.5536e-5
while reader.isConnected:  # as long as the reader is connected...
	candidates = []
	dat = queue.receive()
	n_candidates_remaining = dat[1]
	if n_candidates_remaining != 10000:
		candidates.append(unpack_message(dat))
	print("mesg type ", dat[1])
	print(unpack_message(dat))
	if n_candidates_remaining != 10000:
		for i in range(n_candidates_remaining - 1):
			print("receiving")
			dat = queue.receive()
			print("received")
			candidates.append(unpack_message(dat))
			print(unpack_message(dat))
	print(1)
	dy_norm = read_buffer(reader)
	for i in range(len(
			candidates)):  # for each candidate, calculate what part of data to save and put it
		# in an h5 file
		s1 = int(candidates[i][2]) - int(candidates[i][0]) - 1000
		s1 = s1 * (s1 > 0)
		s2 = min(s1 + int(disp_delay(float(candidates[i][6]), dt, 1.53, 1.28) + 1) + 2 ** int(
			candidates[i][4]) + 1000, 200000)
		save_cand = np.array([dy_norm[:, s1:s2], candidates[i]])
		save_cand[1][-1] = np.string_(save_cand[1][-1])
		save_cand[1][-5] = np.string_(save_cand[1][-5])
		adict = dict(data=save_cand[0], metadata=save_cand[1])
		with h5py.File('/home/user/candidates_train/candidates.h5', 'a') as hf:
			grp = hf.create_group('candidate_%s_%s' % (int(candidates[i][2]), i))
			for k, v in adict.items():
				grp.create_dataset(k, data=v)
		print("Saving candidate %s" % candidates[i][2])
	count += 1
reader.disconnect()  # disconnect from the buffer
