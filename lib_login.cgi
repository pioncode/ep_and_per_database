#!/bin/perl

use CGI qw(:standard);
use CGI::Cookie;
use DBI;
use Digest::SHA1 qw(sha1_hex);
#require 'getuid.pl';

@weekDays = qw(Sun Mon Tue Wed Thu Fri Sat Sun);
($second, $minute, $hour, $dayOfMonth, $month, $yearOffset, $dayOfWeek, $dayOfYear, $daylightSavings) = localtime();
$thisyear = 1900 + $yearOffset;
$month++;

$thisip=$ENV{REMOTE_ADDR};
$challenge=sha1_hex($thisip);  # not a great idea - should be a number that changes, but good enough for now

$jscript =<<END;
function doChallengeResponse() {
   str = document.login_form.user.value.toLowerCase() + ":" +
   document.login_form.userpass.value + ":" + "$challenge";
 
   document.login_form.userpass.value = "";
   document.login_form.challenge.value = "";
   document.login_form.response.value = hex_sha1(str);
   return false;
}
END

  #document.login_form.challenge.value;
print header, start_html(-title=>'Pion librarian login', -script=>[{ -src=>'sha1.js'},{ -code=>$jscript}], -style=>'pion.css');

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
	<div class="left">Pion usage statistics login</div>

	<div class="center"></div>
	<div class="right"></div>
	</font>
      </div>
END
#"
#print p, "<a href=\"http://www.pion.co.uk\"><img src=\"Images/right_ban.gif\" alt=\"Pion Ltd\" /></a>";
# print h1('Pion usage statistics login');


#if (get_uid()){
  #print p,"hello";
 
#  print  p,"You are already logged in as $username. <a href='logout.cgi'>Logout.</a>",end_html;
#}
#else {
  #print p, "login page";
  #print p, "challenge=$challenge\n" ;
  print p, 'This facility is for serials librarians only and is not intended for end users.';
  print p, 'Your browser must support Javascript and cookies.';
  print <<END;
<p>  
<form action="usagelogin_test.cgi" method="post" name="login_form" onSubmit="doChallengeResponse()">
<input type="hidden" name="challenge" value="$challenge">
<input type="hidden" name="response" value="">
Registered e-mail address: <br><input type="text" name="user"><br>
Password: <br><input type="password" name="userpass"><br>

<input type="submit" value="Login">&nbsp;<input type="reset">
</form> 
<div id="footer"><div class="left"></div>

<div class="right">Copyright &copy; $thisyear Pion Ltd.</div>
      </div>
      </div>
    </div>
END
print end_html;
#}

sub get_uid(){

  my %cookies = CGI::Cookie->fetch();

  if ($cookies{user} && $cookies{auth}) {
    $dbh=DBI->connect("dbi:Pg:dbname=journals;host=localhost;port=5432", "jon", "")||die "couldn't connect";
    $username=$cookies{user}->value; 
    my $sth=$dbh->prepare("select uid,token from usagepasswd where email='$username'");
    
    #print p, "select uid,token from passwd where username='$username'";
    $sth->execute();
    my ($uid,$token)=$sth->fetchrow();
    
    my $auth_string = sha1_hex($cookies{user}->value . ":" . $token);
    #  print p, $cookies{user}, p, $cookies{auth}, p, $auth_string;
    #}
    
    #print p, $auth_string,p,$cookies{auth}->value;
    
    if ($auth_string eq $cookies{auth}->value){
      return $uid;
    }
    else {
      return 0;
    }
  } 
  else {
    return 0;
  }
}

