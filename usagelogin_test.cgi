#!/bin/perl

# login.cgi
# experimenting with cookies

# idea:  if no cookie, check DB num_changes. If num_changes=0: first-time login in, authenticate and save data cookie to user, set num_changes=1. Next time, if user/password/token match, then auto-login. If no cookie and num_changes>0: either valid user on diff machine/browser or user with borrowed password. If num_changes is low, change token, num_changes++, authenticate. Block access if num_changes is too high within a specified period (use timestamp).



use CGI qw(:standard -no_xhtml);
use CGI::Cookie;
use DBI;
use Digest::SHA1 qw(sha1_hex);
require 'usagegetuid.pl';

@weekDays = qw(Sun Mon Tue Wed Thu Fri Sat Sun);
($second, $minute, $hour, $dayOfMonth, $month, $yearOffset, $dayOfWeek, $dayOfYear, $daylightSavings) = localtime();
$thisyear = 1900 + $yearOffset;
$month++;
$dbh= DBI->connect("dbi:Pg:dbname=journals;host=localhost;port=5432", "jon", "")||die "couldn't connect";

$user=param('user');
#$auth=param('auth');   # would be better to use javascript to make encrypted digest
$userpass=param('userpass');
$response=param('response');


$sth=$dbh->prepare("select uid,passwd,token,name,clirefs from usagepasswd where email='$user'");
$sth->execute() || die;
($uid,$password,$token,$name,$clirefs)=$sth->fetchrow();


$thisip=$ENV{REMOTE_ADDR};  #store ip to allow downloads of selected pdf?
                              #CAUTION: will allow all NAT users to download!
$response_calc=sha1_hex(lc($user).':'.$password.':'.sha1_hex($thisip));

# if $response, use that, otherwise use plaintext $userpass 
if(($response eq $response_calc || $userpass eq $password) && $uid){

  $lower=100000; 
  $upper=5000000; 
  $random = int(rand( $upper-$lower+1 ) ) + $lower;
  $token=$random; # random number, store in DB
  $dbh->do("update usagepasswd set token=$token, ip='$thisip' where uid=$uid")||die;
  
  # create 2 cookies to be sent in HTTP header (pretty secure)
  my $cookie1 = CGI::Cookie->new(-name => "user", 
                                 -value => $user);
  my $cookie2 = CGI::Cookie->new(-name => "auth",
                                 -value => sha1_hex($user . ":" . $token));
                                 
  print header(-cookie=>[ $cookie1, $cookie2 ]);
  
  print start_html(-title=>'Pion usage statistics login', -style=>'pion.css');
  print <<END;
   <div id="header">

      <a href="http://www.pion.co.uk"><img src="Images/right_ban_crop.gif" alt="Pion" class="logo" /><img src="Images/ion.gif" alt="Pion" class="logo" height=56 /></a>
      <a href="http://www.pion.co.uk"><img src="Images/right_band.gif" alt="" class="pionlogo" /></a>
    </div>
    <div id="total">
      <div id="top-buttons">
	<div class="topnavigation">
	  <ul>
	    <li><a href="librarians.html" title="Information for librarians">For&nbsp;librarians</a></li>

	    <li><a href="index.html" title="Go to Pion ltd homepage">Pion&nbsp;homepage</a></li>
	  </ul>
	</div>
      </div>
      <div id="title">
	<font size=4>
	<div class="left">Usage statistics</div>

	<div class="center"></div>
	<div class="right"></div>
	</font>
      </div>
END
#" 
  # grab the user's cookies
  #my %cookies = CGI::Cookie->fetch();
  
  #if ($cookies{user} and $cookies{auth}) {
  #  my $auth_string = sha1_hex($cookies{user}->value . ":" . $token);
  #  print p, $cookies{user}, p, $cookies{auth}, p, $auth_string;
  #}
  #print p, "<a href=\"http://www.pion.co.uk\"><img src=\"Images/right_ban.gif\" alt=\"Pion Ltd\" /></a>";
#print h1('Pion usage statistics');
  #print p, "Cleartext password accepted - in future, please enable JavaScript on your browser for more security" if $userpass;
  #print p,"You have logged in successfully.", p, "Proceed to <a href='usagestats.cgi'>usage statistics</a>.\n";
  
  print p, "$name";
  $lastyear=$thisyear-1;
  print p, "<a href='usage_download.cgi?uid=$uid&amp;year=$lastyear'>Usage statistics for $lastyear</a> (CSV file)";
  print p, "<a href='usage_download.cgi?uid=$uid&amp;year=$thisyear'>Usage statistics for $thisyear</a> (CSV file)" if $month>1;
  $clirefs =~ s/ /,/g;
  #print "select ip,deny from access where client in ($clirefs);";
  $sth=$dbh->prepare("select distinct ip,deny from access where client in ($clirefs);");
  $sth->execute() || die;
  print p, "<font size='-1'>Your registered IP address ranges (in <a href='http://en.wikipedia.org/wiki/Classless_Inter-Domain_Routing'>CIDR</a> format) are as follows:";
  while(($ip,$deny)=$sth->fetchrow()){
    print br, "$ip";
    print "(access denied from this address)" if $deny;     
  }
  print '</font>';
  print "<div id=\"footer\"><div class=\"left\"></div>

<div class=\"right\">Copyright &copy; $thisyear Pion Ltd.</div>
      </div>
      </div>
    </div>
";    
    
  print end_html;
}
else {
  print header;
  print start_html(-title=>'Pion login failed', -style=>'pion.css');
    print <<END;
   <div id="header">

      <a href="http://www.pion.co.uk"><img src="Images/right_ban_crop.gif" alt="Pion" class="logo" /><img src="Images/ion.gif" alt="Pion" class="logo" height=56 /></a>
      <a href="http://www.pion.co.uk"><img src="Images/right_band.gif" alt="" class="pionlogo" /></a>
    </div>
    <div id="total">
      <div id="top-buttons">
	<div class="topnavigation">
	  <ul>
	    <li><a href="librarians.html" title="Information for librarians">For&nbsp;librarians</a></li>

	    <li><a href="index.html" title="Go to Pion ltd homepage">Pion&nbsp;homepage</a></li>
	  </ul>
	</div>
      </div>
      <div id="title">
	<font size=4>
	<div class="left">Pion usage statistics</div>

	<div class="center"></div>
	<div class="right"></div>
	</font>
      </div>
END
#"
  #print "userpass=$userpass   password=$password\n";
  #print p, "<a href=\"http://www.pion.co.uk\"><img src=\"Images/right_ban.gif\" alt=\"Pion Ltd\" /></a>";
  print h1('Login failed');
  print p,"Unfortunately your username/password have not been recognised. <a href='lib_login.cgi'>Login.</a> \n";
  print "\$response=$response<br>\$response_calc=$response_calc\n\$challenge=".sha1_hex($thisip);  
     print "<div id=\"footer\"><div class=\"left\"></div>

<div class=\"right\">Copyright &copy; $thisyear Pion Ltd.</div>
      </div>
      </div>
    </div>
";    
  
  print end_html; 
}


