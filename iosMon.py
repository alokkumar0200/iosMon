from paramiko import SSHClient
import time, sys, re


def sshConnect(hostname, user, password):
	ssh = SSHClient()
	print(hostname, user, password)
	ssh.load_system_host_keys()
	ssh.connect(hostname, username=user, password=password)
	return ssh
	# ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command('ls')
	# print(ssh_stderr.read(), ssh_stdout.read())
	# ssh.close()

def findDatabase(ssh, path='/'):
	databases = []
	sizes = []
	ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command('for x in $(find '+path+' -type f \\( -name *.db -o -name *.sqlite3 -o -name *.sqlite -o -name *.plist -o -name *.dat -o -iname \"*.realm\" \\) 2>/dev/null); do echo "$x";done')
	for x in ssh_stdout.read().decode().replace('Application\n', 'Application ').strip('\n').split('\n'):
		# print(x,'hello')
		_, ssh_stdout, ssh_stderr = ssh.exec_command('md5sum \"'+x+'\"')
		# print(ssh_stderr.read().decode())
		databases.append(x)
		sizes.append(re.search('[0-9a-z]+',ssh_stdout.read().decode().replace('\n','')).group(0))
	return databases,sizes


def main():
	first = True
	databases = []
	sizes=[]
	tmpSizes=[]
	tmpData=[]

	if len(sys.argv)<4:
		print("[!] Error.")
		print("[!] Syntax: python iosMon.py <hostname_of_ios_device> <ssh_user> <app_sandbox_path>")
	else:
		delay=3
		hostname=sys.argv[1]
		user=sys.argv[2]
		path=sys.argv[3]
		if len(sys.argv)==4:
			delay=3
		if len(sys.argv)==5:
			delay=sys.argv[4]
		#'/var/mobile/Containers/Data/Application/DC8D3D2C-4CB0-4E83-8643-A12F151CDFBD'
		password = input("[?] Password for ssh: ")
		try:
			ssh = sshConnect(hostname,user, password)
		except:
			print("[!] Authentication Failure.")
			sys.exit(1)
		while True:
			try:
				if first != True:
					tmpData,tmpSizes = findDatabase(ssh, path)
					if len(tmpData) > len(databases):
						print('[*] Newly Added Files:')
						for newData in tmpData:
							if newData not in databases:
								print(newData)
								databases.append(newData)
								sizes.append(tmpSizes[tmpData.index(newData)])
					elif len(tmpData) < len(databases):
						print('[*] Below Files Got Deleted.')
						for deletedData in databases:
							if deletedData not in tmpData:
								print(deletedData)
								sizes.pop(databases.index(deletedData))
								databases.pop(databases.index(deletedData))
					elif len(tmpSizes)==len(sizes) and sizes !=tmpSizes:
						print('[*] Below Files Got Changed.')
						for originalData,originalSize in zip(databases, sizes):
							if tmpSizes[tmpData.index(originalData)] != sizes[databases.index(originalData)]:
								print(originalData)
						databases=tmpData
						sizes=tmpSizes
					else:
						pass
				else:
					databases,sizes = findDatabase(ssh, path)
					first = False
					print("[*] Databases found are below.")
					for x in databases:
						print(x)
				time.sleep(delay)
			except:
				ssh.close()
				print('[!] User Interrupted.')
				break

if __name__ == '__main__':
	main()