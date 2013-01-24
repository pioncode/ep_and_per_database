#!/bin/perl

$ip=$ENV{REMOTE_ADDR};

unless ($ip =~ /^85\.119\.146\./ || $ip eq '62.49.248.163'){exit}

use DBI;
use CGI qw(:standard -no_xhtml);
$dbh = DBI->connect("dbi:Pg:dbname=journals;host=localhost;port=5432", "jon", "")||die "couldn't connect";
$sth=$dbh->prepare("select paperid from papers where journal='P' and paperid>='p6010' and volume>=36 and paperid ~* 'p[0-9]';") || die;

$sth->execute()||die "Can't execute query\n";

print header(-type=>'text/plain'); 
while (($paperid)=$sth->fetchrow()){
  print "$paperid\n";
}