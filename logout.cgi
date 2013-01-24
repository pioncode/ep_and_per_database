#!/bin/perl

use CGI qw(:standard);
use CGI::Cookie;
use DBI;
require 'getuid.pl';

print header, start_html(-title=>'Logout');
$dbh=DBI->connect("dbi:Pg:dbname=journals;host=localhost;port=5432", "jon", "")||die "couldn't connect"; 
$uid=get_uid();

if ($uid){
  $dbh->do("update passwd set token=NULL where uid=$uid");
  print  p,"Your now logged out";
}
else {
  print "You are not logged in";
}

print end_html;
