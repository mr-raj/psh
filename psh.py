#rsha541
#5621877
#rajneel sharma
import shlex
import os
import sys
import subprocess
import traceback
import signal

hist = []

class PShell():
    finished_jobs = []
    job_list = []
    job_count = 1
    
    global hist
    startDir = os.getcwd()
    
    def read_loop(self):
           
        while True:
            
            try:  
                line = input('psh> ')
            except EOFError:
                os.kill(0,signal.SIGTERM)

            is_file_input = not os.isatty(sys.stdin.fileno())
            if (is_file_input):
               
               print(line)
  
            
            hist.append(line)
            words = self.word_list(line)
                
            command = words[0]
            self.func(command, words)

            
    def word_list(self, line):
        """Break the line into shell words.
        """
        lexer = shlex.shlex(line, posix=True)
        lexer.whitespace_split = False
        lexer.wordchars += '#$+-,./?@^='
        args = list(lexer)
        return args
    
    
    def func(self, request, wordz):
          try:
                
                if len(self.job_list) != 0: # Checks to see if jobDone
                        for single_job in self.job_list:
                            pid = single_job.pid
                            process = subprocess.Popen(['ps', '-p', str(pid), '-o', 'state='], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                            result, error = process.communicate()
                            if result.decode()[0] == "Z":
                                  self.finished_jobs.append(single_job)
                        for pop_job in self.finished_jobs:
                            if pop_job in self.job_list:
                                  indexpop_job = self.job_list.index(pop_job)
                                  self.job_list.pop(indexpop_job)  
                

                if ("&" in wordz):
                    amper = 1
                    del(wordz[wordz.index('&')])
                else:
                    amper = 0


                child = os.fork()
                if child == 0:
                  
                    if("|" in wordz): #if shlexed input list contains '|'
                      
                        if ("|" in wordz[0] or "|" in wordz[wordz.index('|')+1] or "|" in wordz[len(wordz)-1]): #handles invalid pipe use
                           print('Invalid use of pipe "|".')
                          
         
                        elif ("|" in wordz):
                           while '|' in wordz:
                              nextPipe = wordz.index('|')
                               
                              
                              pIn, pOut = os.pipe() 
                  
                              if (os.fork() == 0):  
                     
                                os.dup2(pOut, 1)
                                os.close(pIn)
                                os.execvp(wordz[0], wordz[0:nextPipe])
                                
                            
                              wordz = wordz[nextPipe+1:]

                              os.dup2(pIn, 0)
                              os.close(pOut)

                           os.execvp(wordz[0], wordz[0:nextPipe])
                           

                    elif request == "cd":
                           self.chdir(wordz)
                         
                    elif request == "pwd":
                           
                           print (os.getcwd())
                        
                    elif request == "h" or request == "history":
                        
                          self.history(wordz)
                    elif request == "jobs":
                          self.jobs(wordz)
                    
                    else:
                           
                           os.execvp(request, wordz)
                else:
                   
                   if amper == 0:
                       if self.checkpro(os.getpid()) == True:
                          os.waitpid(child, 0)
                   else:
                     
                       os.waitpid(child, os.WNOHANG)
                       tempLine = " ".join(wordz)
                       yung_job = job(child, self.job_count, tempLine)
                       self.job_list.append(yung_job)
                      
                       print( "[%s]	%s " % (self.job_count,child))
                       self.job_count += 1
                
                while (len(self.finished_jobs) != 0):
                          for done in self.finished_jobs:
                            print("[%s]     Done              %s"  % (done.job_number, done.command))
                            self.finished_jobs.pop(self.finished_jobs.index(done))
                       
                if (len(self.job_list) == 0):
                    self.job_count = 1   
                                         
          except OSError:
                 print('Caught an OSError.')
                


    def jobs(self, args):
        for job in self.job_list:
          pid = job.pid
          ps = subprocess.Popen(['ps', '-p', str(pid), '-o', 'state='], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
          result, error= ps.communicate()
          if result.decode() != '':

                state = result.decode()[0]

                if "Z" in state:
                    state = "Done"
                elif "R" in state:
                    state = "Running"
                elif "S" in state:
                    state = "Sleeping"
                elif "T" in state:
                    state = "Stopped"

                
                print('[{}] <{}> {}'.format(job.job_number, state, job.command))

    def checkpro(self, process_id):
        try:
           os.kill(process_id, 0)
           return True
        except OSError:
           return False
        
              
    def chdir(self, words):  
       
         try:
            if len(words) > 1:
                os.chdir(words[1])
            else:
                os.chdir(self.startDir)
         except OSError:
                print('No such file or directory.')


    def history(self, thang):
       if len(thang) > 1:
              
              
              comm = self.word_list(hist[int(thang[1])-1])
              hist.pop()
              hist.append(' '.join(comm))
              
              self.func(comm[0], comm)
       else:
              
              for i in range(len(hist)-10, len(hist)):
                     if i > -1:
                              print (str(i+1)+":"+hist[i])      
class job(): 
       pid = 0
       job_number = 0
       command = None

       def __init__(self, pid, job_number, command):
            self.pid = pid
            self.job_number = job_number
            self.command = command


my_shell = PShell()
try:
	my_shell.read_loop()
except EOFError:
       sys.exit()
except ValueError:
	     sys.exit()
except KeyboardInterrupt:
       sys.exit()

