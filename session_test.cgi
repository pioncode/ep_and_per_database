#!/bin/perl

# session.cgi
# experimenting with cookies

#
use CGI qw(:standard -no_xhtml);
use CGI::Cookie;
use DBI;
require "getuid.pl";

use Digest::SHA1 qw(sha1_hex);

$dbh= DBI->connect("dbi:Pg:dbname=journals;host=localhost;port=5432", "jon", "")||die "couldn't connect";


print header(-title=>'Session test');
  
print start_html;
print "Hello";
$uid=get_uid('A.*05');

if ($uid){ 
  print p, "Access granted. Welcome $username (uid=$uid)"
}
else {
  print p, "Access denied",p, "Please <a href=\"login_form.cgi\">login</a>";
}

print end_html;


