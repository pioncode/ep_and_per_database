#!/bin/perl

use CGI qw(:standard -no_xhtml);
$URL= $ENV{'REDIRECT_URL'};
$URL=~/.*\/(.+)\.pdf/;
$paperid=$1;
print header;
if ($paperid){
  print "<HTML>\n<head>\n<meta http-equiv='REFRESH' content='0;url=/abstract.cgi?id=$paperid'></HEAD>";
  print h1('Redirecting...');
  print p, "If you are not redirected to the abstract page in a few seconds, <a href='/abstract.cgi?id=$paperid'>Please click here</a>";
}
else {
  print "<HTML>\n<head>\n<meta http-equiv='REFRESH' content='0;url=/'></HEAD>";
  print h1('Redirecting...');
  print p, "If you are not redirected to the abstract page in a few seconds, <a href='/'>Please click here</a>";
}

print end_html;

