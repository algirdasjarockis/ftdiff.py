#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

#
# tool, that compares file tree by calculating file hashes
#

import hashlib
import os, sys
import argparse

class Config:
	# list of hashes
	hashes = ['sha1', 'md5']
	
	# default hash index
	defaultHash = 0
	
	# file read block size in bytes
	fileReadBlockSize = 1024

	
#
# get checksum of given file
#
# @param string filePath - path of file
# @return string - checksum of file (empty on error)
#
def checksumFile(filePath):
	with open(filePath, 'rb') as fp:
		h = hashlib.new(Config.hashes[Config.defaultHash])
		while True:
			block = fp.read(Config.fileReadBlockSize)
			if not block:
				break
				
			h.update(block)
			
	return h.hexdigest()
			
			
#
# return flattened tree of dir contents
#
# @param string dirPath - path of dir
# @return dict of dicts
#
def getFlatFileTree(dirPath, verbose=False):
	ft = {}
	for root, dirs, files in os.walk(dirPath):
		if verbose:
			print(" - Reading '{0}'".format(root))
		
		innerDir = root.replace(dirPath, '/')
		ft[innerDir] = {
			'root': root,
			'dirs': dirs,
			'files': files		
		}
		
	return ft
		
if __name__ == '__main__':
	parser = argparse.ArgumentParser(prog='ftdiff', description='File tree diff tool')
	parser.add_argument('directory_path', nargs=2)
	parser.add_argument('-v', '--verbose', required=False, dest='verbose', action='store_true', help='show processing information')
	parser.add_argument('-f', '--full-diff', required=False, dest='fullDiff', action='store_true', help="set this flag to do full diff - don't stop on first error")
	args = parser.parse_args()
	
	if not os.path.isdir(args.directory_path[0]):
		print("[E] Path '{0}' does not exist".format(args.directory_path[0]))
		
	if not os.path.isdir(args.directory_path[1]):
		print("[E] Path '{0}' does not exist".format(args.directory_path[1]))
		
	tree1 = getFlatFileTree(args.directory_path[0], args.verbose)
	tree2 = getFlatFileTree(args.directory_path[1])
	
	# compare
	for i in tree1.keys():
		item = tree1[i]
		if i not in tree2.keys():
			print "[E] Missing directory '{0}'".format(i)
			if not args.fullDiff:
				sys.exit(1)
				
			continue
		
		# sets of file(dir) names
		fsSet1 = set(item['files'] + item['dirs'])
		fsSet2 = set(tree2[i]['files'] + tree2[i]['dirs'])
		
		# difference of sets
		diff = fsSet1.symmetric_difference(fsSet2)
		
		if diff:
			# file struct differs
			print "[E] File structure does not match! Items that make difference: ", diff
			if not args.fullDiff:
				sys.exit(1)
		else:
			# file structure is ok, need to checksum files
			for fName in item['files']:
				checksum1 = checksumFile(item['root'] + '/' + fName)
				checksum2 = checksumFile(tree2[i]['root'] + '/' + fName)
				
				if checksum1 != checksum2:
					print("[E] Checksums for '{0}' and '{1}' doesn't match!".format(item['root'] + '/' + fName, tree2[i]['root'] + '/' + fName))
					if not args.fullDiff:
						sys.exit(1)
	
	print("\nFinished")
	sys.exit(0)
	
	
	
