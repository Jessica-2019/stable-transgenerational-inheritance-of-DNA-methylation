import sys, math, glob, multiprocessing, subprocess, os, bisect, random
from bioFiles import *

# Usage: python weighted_meth_by_pos_pe.py [-o=out_id] [-v=min_cov] [-p=num_proc] <pos_list> <allc_path> <sample_name> [sample_name]*
# output each row is a sample, each column is a position
# each chrm gets a file

MINCOV = 3
NUMPROC = 1

def processInputs( allcPath, posFileStr, sampleNamesAr, outID, minCov, numProc ):
	print( 'Position file:', os.path.basename( posFileStr ) )
	print( 'AllC path:', allcPath )
	print( 'Samples:', ', '.join(sampleNamesAr ) )
	print( 'Minimum coverage:', minCov )
	info = '#from_script: weighted_meth_by_pos_pe.py; pos_file: {:s}; samples: {:s}; min_cov: {:d}'.format( os.path.basename( posFileStr ), ','.join( sampleNamesAr ), minCov )
	# get positions with chrm
	posDict = getPositions( posFileStr )
	
	# check files
	suc = checkFiles( allcPath, sampleNamesAr, list( posDict.keys() ) )
	if not suc:
		exit()
	
	pool = multiprocessing.Pool( processes=numProc )
	print( 'Begin processing with', numProc, 'processors' )
	# loop through chrms
	for chrm in sorted(posDict.keys()):
		print( 'Processing', chrm )
		files = [ os.path.normpath('{:s}/allc_{:s}_{:s}.tsv'.format( allcPath, sample, chrm ) ) for sample in sampleNamesAr ]
		posAr = posDict[chrm]
		# multiprocess getting positions from allc files
		results = [ pool.apply_async(processFile, args=(f, posAr, minCov) ) for f in files ]
		chrmDictAr = [ p.get() for p in results ]
		wmMat = []
		naSet = set()
		# reorder results
		for d in chrmDictAr:
			wmMat.append( d['w'] )
			naSet.update( d['n'] )
		#print( naSet )
		prevLen = len( posAr )
		cleanMat, cleanPos = cleanMatrixNA( wmMat, naSet, posAr )
		#print( posAr[:10] )
		print( 'Removed', len(naSet), 'low coverage positions:', prevLen, '->', len(cleanPos) )
		# write outputs
		outFileStr = '{:s}_wm_pos_{:s}.tsv'.format( outID, chrm )
		print( 'Writing results for', chrm, 'to', outFileStr )
		writeOutput( outFileStr, cleanMat, cleanPos, sampleNamesAr, info )
		# clean data structures
		del( chrmDictAr, files, posAr, wmMat, naSet, cleanMat, cleanPos, results )
	# end for
	print( 'Done' )

def getPositions( posFileStr ):
	
	# check exists
	suc = os.path.isfile( posFileStr )
	if not suc:
		print( 'ERROR: position file', posFileStr, 'does not exist' )
		exit()
	posFile = open( posFileStr, 'r' )
	outDict = {}
	for line in posFile:
		if line.startswith( '#' ):
			continue
		lineAr = line.rstrip().split()
		try:
			chrm = lineAr[0]
			pos = int( lineAr[1] )
			if outDict.get(chrm) == None:
				outDict[chrm] = []
			outDict[chrm] += [ pos ]
		except ValueError:
			pass
	# end for line
	posFile.close()
	# sort positions lists just to be sure
	for key in outDict.keys():
		outDict[key].sort()
	return outDict

def checkFiles( allcPath, sampleNamesAr, chrmList ):
	for sample in sampleNamesAr:
		for chrm in chrmList:
			if os.path.isfile( os.path.normpath('{:s}/allc_{:s}_{:s}.tsv'.format( allcPath, sample, chrm ) ) ) == False:
				print( 'ERROR: allC file for sample {:s} chrm {:s} not found'.format( sample, chrm ) )
				return False
	return True

def processFile( allcFileStr, posAr, minCov ):
	print(' reading {:s}'.format( os.path.basename(allcFileStr) ) )
	# used to store methylation values
	wmAr = [-1] * len(posAr)
	naAr = []
	allcFile = open( allcFileStr, 'r' )
	for line in allcFile:
		lineAr = line.rstrip().split('\t')
		# (0) chr (1) pos (2) strand (3) mc class (4) mc_count (5) total
		# (6) methylated
		if len(lineAr) < 7 or lineAr[6].isdigit() == False:
			continue
		pos = int( lineAr[1] )
		i = bisectIndex( posAr, pos )
		# we want this position
		if i != None:
			wm = float( lineAr[4] ) / float( lineAr[5] )
			wmAr[i] = wm
			naAr += [i] if int(lineAr[5]) < minCov else []
	# end for line
	allcFile.close()
	return {'w': wmAr, 'n': set( naAr ) }

def bisectIndex( a, x ):
	i = bisect.bisect_left( a, x )
	if i != len( a ) and a[i] == x:
		return i
	else:
		return None

def cleanMatrixNA( wmMat, naSet, posAr ):
	# reverse order positions to remove
	rmPos = sorted(list( naSet ), reverse = True )
	# loop through arrays in wmMat
	for ar in wmMat:
		# loop through rmPos
		for rp in rmPos:
			ar.pop( rp )
	# end for ar
	# clean posAr
	for rp in rmPos:
		posAr.pop( rp )
	return wmMat, posAr

def writeOutput( outFileStr, cleanMat, cleanPos, sampleNamesAr, info ):
	outFile = open( outFileStr, 'w' )
	outFile.write( info + '\n' + 'sample\tpos\twei.meth\n' )
	# loop through samples
	for i in range(len(sampleNamesAr ) ):
		# loop through positions
		for j in range(len(cleanPos)):
			outFile.write( '{:s}\t{:d}\t{:.6f}\n'.format( sampleNamesAr[i], cleanPos[j], cleanMat[i][j] ) )
	# end for i
	outFile.close()

def parseInputs( argv ):
	minCov = MINCOV
	numProc = NUMPROC
	outID = 'out'
	startInd = 0
	
	for i in range(min(3,len(argv))):
		if argv[i].startswith( '-o=' ):
			outID = argv[i][3:]
			startInd += 1
		elif argv[i].startswith( '-v=' ):
			try:
				minCov = int( argv[i][3:] )
				startInd += 1
			except ValueError:
				print( 'ERROR: minimum coverage must be integer' )
				exit()
		elif argv[i].startswith( '-p=' ):
			try:
				numProc = int( argv[i][3:] )
				startInd += 1
			except ValueError:
				print( 'ERROR: number of processors must be integer' )
				exit()
		elif argv[i] in [ '-h', '--help', '-help']:
			printHelp()
			exit()
		elif argv[i].startswith( '-' ):
			print( 'ERROR: {:s} is not a valid option'.format( argv[i] ) )
			exit()
	# end for
	
	posFileStr = argv[startInd]
	allcPath = argv[startInd+1]
	sampleNamesAr = []
	for j in range(startInd+2, len(argv)):
		sampleNamesAr += [ argv[j] ]
	processInputs( allcPath, posFileStr, sampleNamesAr, outID, minCov, numProc )

def printHelp():
	print ("Usage: python weighted_meth_by_pos_pe.py [-o=out_id] [-v=min_cov] [-p=num_proc] <pos_list> <allc_path> <sample_name> [sample_name]*")

if __name__ == "__main__":
	if len(sys.argv) < 4:
		printHelp()
	else:
		parseInputs( sys.argv[1:] )
