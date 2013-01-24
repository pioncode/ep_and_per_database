#!/bin/perl

# login.cgi
# experimenting with cookies

# idea:  if no cookie, check DB num_changes. If num_changes=0: first-time login in, authenticate and save data cookie to user, set num_changes=1. Next time, if user/password/token match, then auto-login. If no cookie and num_changes>0: either valid user on diff machine/browser or user with borrowed password. If num_changes is low, change token, num_changes++, authenticate. Block access if num_changes is too high within a specified period (use timestamp).



use CGI qw(:standard -no_xhtml);
use CGI::Cookie;
use DBI;
use Digest::SHA1 qw(sha1_hex);
require 'getuid.pl';

$dbh= DBI->connect("dbi:Pg:dbname=journals;host=localhost;port=5432", "jon", "")||die "couldn't connect";

#my $SECRET = "my secret garden"; 
#$token='654322'; # from DB

#$validuser='fred';
#$validpasswd='test';

$user=param('user');
#$auth=param('auth');   # would be better to use javascript to make encrypted digest
$userpass=param('userpass');
$response=param('response');


$sth=$dbh->prepare("select uid,password,token from passwd where username='$user'");
$sth->execute() || die;
($uid,$password,$token)=$sth->fetchrow();


$thisip=$ENV{REMOTE_ADDR};  #store ip to allow downloads of selected pdf?
                              #CAUTION: will allow all NAT users to download!
$response_calc=sha1_hex(lc($user).':'.$password.':'.sha1_hex($thisip));

# if $response, use that, otherwise use plaintext $userpass 
if(($response eq $response_calc || $userpass eq $password) && $uid){

  $lower=100000; 
  $upper=5000000; 
  $random = int(rand( $upper-$lower+1 ) ) + $lower;
  $token=$random; # random number, store in DB
  $dbh->do("update passwd set token=$token, ip='$thisip', time=now() where uid=$uid")||die;
  
  # create 2 cookies to be sent in HTTP header (pretty secure)
  my $cookie1 = CGI::Cookie->new(-name => "user", 
                                 -value => $user);
  my $cookie2 = CGI::Cookie->new(-name => "auth",
                                 -value => sha1_hex($user . ":" . $token));
                                 
  print header(-cookie=>[ $cookie1, $cookie2 ]);
  
  print start_html(-title=>'Pion login');
  
  # grab the user's cookies
  #my %cookies = CGI::Cookie->fetch();
  
  #if ($cookies{user} and $cookies{auth}) {
  #  my $auth_string = sha1_hex($cookies{user}->value . ":" . $token);
  #  print p, $cookies{user}, p, $cookies{auth}, p, $auth_string;
  #}
  print p, "<a href=\"http://www.pion.co.uk\"><img src=\"Images/right_ban.gif\" alt=\"Pion Ltd\" /></a>";
print h1('Pion login');
  print p, "Cleartext password accepted - in future, please enable JavaScript on your browser for more security" if $userpass;
  print p,"You have logged in successfully.", p, "Proceed to <a href='index.html'>website</a>.\n";
  #print p, "<a href='session_test.cgi'>session_test.cgi</a>";
 #print "\$response=$response<br>\$response_calc=$response_calc"; 
  print end_html;
}
else {
  print header;
  print start_html(-title=>'Pion login failed');
  print p, "<a href=\"http://www.pion.co.uk\"><img src=\"Images/right_ban.gif\" alt=\"Pion Ltd\" /></a>";
  print h1('Pion login failed');
  print p,"Login failed. Your username/password has not been recognised. <a href='login_form.cgi'>Login.</a> \n";
 print "\$response=$response<br>\$response_calc=$response_calc\n\$challenge=".sha1_hex($thisip);   
  print end_html; 
}


