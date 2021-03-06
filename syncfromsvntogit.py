#!/usr/bin/python
from sync import *
from getgitlog import *
from getsvnlog import *
from parsegitlog import *
from iscontainsvnorgitlog import *
import commands
import re
import os
import pdb
def main(svn_dir, git_dir):
	err, upinfo = commands.getstatusoutput("cd " + svn_dir + ";svn up")
	if err != 0:
		print "svn up failed"
		return
	if not ("At revision" in upinfo):
		print "svn up wrong:", upinfo
		return
	SvnLogS = GetSvnLog(svn_dir)
	if len(SvnLogS) == 0:
		print "Svn Log is null"
		return
	GitLogS = GetGitLog(git_dir)
	if len(GitLogS) == 0:
		print "Git Log is null"
		return
	SvnCommitLog = ""
	SvnContainGitCommitIndex, SvnContainGitCommitInfo = IsGitLogInSvnLogS(SvnLogS)
	if SvnContainGitCommitIndex == -1:
		GitContainSvnHeadIndex, GitContainSvnHeadInfo = IsSvnLogInGitLogS(GitLogS)
		print "GitContainSvnHeadIndex:", GitContainSvnHeadIndex
		for i in range(0, GitContainSvnHeadIndex):
			SvnCommitLog = SvnCommitLog + GitLogS[i]['body']
	else:
		GitLogInSvnLog = ParseGitLog(SvnContainGitCommitInfo[0]['body'])
                FirstGitLogCommit = GitLogInSvnLog[0]['commit']
		for i in range(0, len(GitLogS)):
			if FirstGitLogCommit != GitLogS[i]['commit']:
				SvnCommitLog = SvnCommitLog + GitLogS[i]['body']
			else:
				break
		
		if SvnCommitLog == '':
			print "Nothing to commit to Svn"
	                return

	SyncDir(git_dir, svn_dir)

	err, SvnAddInfo = commands.getstatusoutput('cd ' + svn_dir + '; svn status | grep "^\?" |sed "s/^\?  *//g" | xargs svn add')
	#if err != 0:
		#print "svn add failed:", SvnAddInfo
		#return
	
	err, SvnDelInfo = commands.getstatusoutput('cd ' + svn_dir + '; svn status | grep "^\!" |sed "s/^\!  *//g" | xargs svn rm')
	#if err != 0:
		#print "svn del failed:", SvnDelInfo
		#return
	fp = open(git_dir + "/.cddiaogitsvntemplogfile.txt", 'w')
	fp.write(SvnCommitLog);
	fp.close()
        commands.getstatusoutput("cd " + svn_dir + "; svn add *")        
	CommitCmd = "cd " + svn_dir + ";svn commit -F " + git_dir + "/.cddiaogitsvntemplogfile.txt"
	print "commitcmd:", CommitCmd
	err, SvnCommitInfo = commands.getstatusoutput(CommitCmd)
        commands.getstatusoutput("cd " + git_dir + ";rm .cddiaogitsvntemplogfile.txt")
	if err != 0:
		print "svn commit error"
		return
	print "commit to svn:", SvnCommitInfo
	err, newlogs = commands.getstatusoutput("cd " + svn_dir + "; svn up")
	print "after commit new version:"
	print newlogs

if __name__ == "__main__":
	if len(sys.argv) != 3:
		if "-h" in sys.argv or "--help" in sys.argv:
                        print "syncfromsvntogit svn_dir git_dir"
			print __doc__
			sys.exit(1)
		errExit(u"invalid arguments!")
	svn_dir = sys.argv[1]
	git_dir = sys.argv[2]
        svn_dir = os.path.abspath(svn_dir)
        git_dir = os.path.abspath(git_dir)
	if os.path.isdir(svn_dir) == False:
		errExit(u"'%s' is not a folder!" % svn_dir)
	if os.path.isdir(git_dir) == False:
		errExit(u"'%s' is not a folder!" % git_dir)
	main(svn_dir, git_dir)
