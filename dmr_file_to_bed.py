import sys, math, glob, multiprocessing, subprocess, os, bisect, random

# Usage: python dmr_file_to_bed.py [-v=score_thresh] [-p=name_prefix] [-o=outID] <in_file>

def processInputs( inFileStr, minScore, namePre, outID ):
	# get outID if necessary
	
	bname = os.path.basename( inFileStr )
	print( 'Input file:', bname )
	print( 'Score threshold:', minScore )
	print( 'Name prefix:', namePre )
	if outID == None:
		ffind = bname.rfind('.tsv' )
		if ffind != -1:
			outID = bname[:ffind].replace('_switches', '' )
		else:
			outID = bname
	outFileStr = outID + '.bed'
	print( 'Output file:', outFileStr )
	print( 'Converting' )
	processFile( inFileStr, outFileStr, minScore, namePre )
	print( 'Done' )
	
def processFile( inFileStr, outFileStr, minScore, namePre ):
	
	inFile = open( inFileStr, 'r' )
	outFile = open( outFileStr, 'w' )
	
	for line in inFile:
		# header
		if line.startswith( '#' ):
			continue
		lineAr = line.rstrip().split( '\t' )
		# (0) index (1) DMR # (2) region (3) switches
		if lineAr[1] == 'DMR':
			continue
		# check score
		if len(lineAr) >= 4 and float(lineAr[3]) < minScore:
			continue
		# parse region
		r1 = lineAr[2].split( ':' )
		chrm = r1[0]
		r2 = r1[1].split('-')
		start = r2[0]
		end = r2[1]
		outAr = [chrm, start, end]
		if namePre == '':
			outAr +=[ lineAr[1] ]
		else:
			outAr += [ '{:s}-{:s}'.format( namePre, lineAr[1] ) ]
		outFile.write( '\t'.join( outAr ) + '\n' )
	# end for line
	inFile.close()
	outFile.close()
			

def parseInputs( argv ):
	minScore = -1
	namePre = ''
	outID = None
	startInd = 0
	
	for i in range(min(3,len(argv)-1)):
		if argv[i].startswith( '-o=' ):
			outID = argv[i][3:]
			startInd += 1
		elif argv[i].startswith( '-v=' ):
			try:
				minScore = float( argv[i][3:] )
				startInd += 1
			except ValueError:
				print( 'ERROR: score threshold must be numeric' )
				exit()
		elif argv[i].startswith( '-p=' ):
			namePre = argv[i][3:]
			startInd += 1
		elif argv[i] == '-h':
			printHelp()
			exit()
		elif argv[i].startswith( '-' ):
			print( 'ERROR: {:s} is not a valid option'.format( argv[i] ) )
			exit()
	# end for
	inFileStr = argv[startInd]
	processInputs( inFileStr, minScore, namePre, outID )
		

def printHelp():
	print( 'Usage: python dmr_file_to_bed.py [-v=score_thresh] [-p=name_prefix] [-o=outID] <in_file>' )
	print( '-v=score_thresh\tmin score to include in output [default -1]' )
	print( '-p=name_prefix\tprefix for naming features [default None]' )
	print( '-o=outID\tidentifer for output file' )
	

if __name__ == "__main__":
	if len(sys.argv) < 2 :
		printHelp()
	else:
		parseInputs( sys.argv[1:] )
