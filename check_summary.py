#!/usr/bin/env python
import os, time, argparse

HOST_STATE_MAP = {"0": "UP", "1": "DOWN"}
STATE_MAP = {"0": "OK", "1": "WARNING", "2": "CRITICAL", "3": "UNKNOWN"}
HOST_TO_SERVICE_STATE_MAP = {"0": "0", "1": "2"}

def parse_status_file(filepath):
   """Parse a nagio status.dat file.  Returns a
   dictionary where the primary keys are the hostnames.  For each
   host all of the services are listed in the 'services' key; the other
   key elements are used for host details."""
   STATUS=open(filepath)
   summary = {}
   while 1:
       line = STATUS.readline()
       if not line:
           break

       line = line.strip()
       if line.startswith("#"):
           # A Comment
           pass

       elif line.find('{') != -1:
           statustype = line[0:line.find('{')]
           if statustype.strip() == "hoststatus":
               # We except host_name and service_description first
               line = STATUS.readline()
               name, hostname = line.split("=", 1)
               name = name.strip()
               hostname = hostname.strip()
               if name != "host_name":
                   continue
               if not summary.has_key(hostname):
                   summary[hostname] = {}
                   summary[hostname]['services'] = {}
               # Now read all the details
               while 1:
                   line = STATUS.readline()
                   if not line:
                       break
                   elif line.find("=") != -1:
                       name, value = line.split("=", 1)
                       name = name.strip()
                       value = value.strip()
                       summary[hostname][name] = value
                   elif line.find("}") != -1:
                       break

           elif statustype.strip() == "servicestatus":
               # We except host_name and service_description first
               line = STATUS.readline()
               name, hostname = line.split("=", 1)
               name = name.strip()
               hostname = hostname.strip()

               line = STATUS.readline()
               name, service_desc = line.split("=", 1)
               name = name.strip()
               service_desc = service_desc.strip()
               if name != "service_description":
                   continue
               summary[hostname]['services'][service_desc] = {}
               # Now read all the details
               while 1:
                   line = STATUS.readline()
                   if not line:
                       break
                   elif line.find("=") != -1:
                       name, value = line.split("=", 1)
                       name = name.strip()
                       value = value.strip()
                       summary[hostname]['services'][service_desc][name] = value
                   elif line.find("}") != -1:
                       break
   return summary

def pretty_print_status(path):
   summary = parse_status_file(path)

   str_out = ""
   state_out = -1

   hosts = summary.keys()
   hosts.sort()
   for host in hosts:
       status = summary[host]
       host_state = HOST_STATE_MAP[status['current_state']]
       if host_state != "UP" and status['problem_has_been_acknowledged'] == "0":
          str_out += "%s: %s, " % (host, host_state)
          state_out = max(state_out, HOST_TO_SERVICE_STATE_MAP[status['current_state']])
       else:
         services = summary[host]['services'].keys()
         services.sort()
         for service in services:
             status = summary[host]['services'][service]
             current_state = STATE_MAP[status['current_state']]
             if current_state != "OK" and ( status['problem_has_been_acknowledged'] == "0"):
                 str_out += "%s/%s: %s, " % (host, service, current_state)
                 state_out = max(state_out, status['current_state'])

   if str_out:                 
    print STATE_MAP[state_out] + " " + str_out[:-2]
   else:
    print "OK all fine"

if __name__ == "__main__":
      parser = argparse.ArgumentParser()
      parser.add_argument("-S", help="Status file path default is /var/cache/nagios3/status.dat", type=str)
      args = parser.parse_args()

      path = "/var/cache/nagios3/status.dat"
      if args.S:
        path = args.S
      
      try:
        pretty_print_status(path)
      except Exception, e:
        print "WARNING", e

