#!/usr/bin/perl -T
# collect email address. If entry not in database, send confirmation email with random number (stored in DB) which contains link to confirm.cgi?id=xx&conf=random_number. Confirm.cgi checks that numbers match, then sets active flag in DB (DB to be dumped and rsync'd to proton4). Another script, remove.cgi?id=xx&conf=random_number deletes row (user is prompted whether to continue and script calls itself with remove.cgi?id=xx&conf=random_number&ok=y)
# If email is already in database, and new journal or warn, as appropriate.
# Each journal needs a separate service.

# create cronjob to delete from emailaddresses where now()-regdate>'2 weeks' and confirmed is false 

$TESTMODE=1;  # disable captch check for testing on proton4 - set to 0 for normal operation!!!

use CGI::Pretty qw/:standard/;
use Mail::SendEasy;
use DBI;
use Captcha::reCAPTCHA;

my $c = Captcha::reCAPTCHA->new unless $TESTMODE;

$db= DBI->connect("dbi:Pg:dbname=emailalert;host=localhost;port=5432", "jon", "") || die;

$email=param('email');
$emailconf=param('emailconf');
$journal=param('journal');
$challenge=param('recaptcha_challenge_field');
$response=param('recaptcha_response_field');

$host=$ENV{'HTTP_HOST'};

@weekDays = qw(Sun Mon Tue Wed Thu Fri Sat Sun);
($second, $minute, $hour, $dayOfMonth, $month, $yearOffset, $dayOfWeek, $dayOfYear, $daylightSavings) = localtime();
$thisyear = 1900 + $yearOffset;
$month++;

%baseurl= (
 "P" => "www.perceptionweb.com",
 "A" => "www.envplan.com",
 "B" => "www.envplan.com",
 "C" => "www.envplan.com",
 "D" => "www.envplan.com"
);

%jname= (
 "P" => "Perception",
 "A" => "Environment and Planning A",
 "B" => "Environment and Planning B: Planning and Design",
 "C" => "Environment and Planning C: Government and Policy",
 "D" => "Environment and Planning D: Society and Space"
);

%bannername= (
 "P" => "p_ban2.gif",
 "A" => "a_ban.gif",
 "B" => "b_ban.gif",
 "C" => "c_ban.gif",
 "D" => "d_ban.gif"
);

exit unless $journal eq 'A' || $journal eq 'B' || $journal eq 'C' || $journal eq 'D' || $journal eq 'P';

# TODO: add captcha

if ($journal eq 'P'){$pubkey='6LcpxwAAAAAAALvPghTLwcJWGU-edxKrGJa5bi58'; $privkey='6LcpxwAAAAAAAJ7jokS9Hq32l28nzcRirNUFK2G5'}
elsif($journal=~/[A-D]/){
  $pubkey='6LfkxgAAAAAAALou3A9QZAMTKvqwjdAfFiaX4ijj'; $privkey='6LfkxgAAAAAAAH21msYa6CRw1tT07aul4FQ0W8ut'
}
elsif($journal eq 'H'){$pubkey='6LflxgAAAAAAAEpO12uWfXd52VBJg1yMH-nMbX0N'; $privkey='6LflxgAAAAAAAK8I2lxGnx3JEc-VNBYQw5p0-qrw'}
else {$pubkey='6LfixgAAAAAAAELRcfnOLvvA6_5IT2Xk5KAxIEmD'; $privkey='6LfixgAAAAAAAFsqiAYC1ftt-HatJ0WWnZVgov_O'}

$captcha=$c->get_html( $pubkey, $err, $ssl, ('theme'=>'white') ) unless $TESTMODE;

my $result = $c->check_answer(
        $privkey, $ENV{'REMOTE_ADDR'},
        $challenge, $response
    ) unless $TESTMODE;
    
$valid_captcha= $result->{is_valid} unless $TESTMODE;

$valid_captcha=1 if $TESTMODE;

$email=~s/\s//g;   # clean this up to prevent SQL hacking
$emailconf=~s/\s//g;

# TODO: If not a valid Pion hostname (eg connecting via a proxy), redirect user to direct site.


print header, start_html(-title=>"Pion email alerting service", -style=>'pion.css', -dtd=>'-//W3C//DTD HTML 4.0 Transitional//EN');

if($journal eq 'P'){
 print <<END;
<div id="header">
    <a href="P.html"><img src="Images/$bannername{$journal}" alt="$jname{$journal}" class="logo" /></a>

    <a href="http://www.pion.co.uk"><img src="Images/right_ban.gif" alt="Pion Ltd" class="pionlogo" /></a>
  </div>
  <div id="total">
    <div id="top-buttons">
      <div class="topnavigation">
	<ul>
	  <li><a href="search.cgi?journal=P." title="Search all papers">Search</a></li>
	  <li><a href="contents.cgi?journal=P&issue=current" title="View latest issue">Current&nbsp;issue</a></li>
	  <li><a href="contents.cgi?journal=P" title="View latest volume">Current&nbsp;volume</a></li>
	  <li><a href="contents.cgi?journal=P&volume=forthcoming" title="View forthcoming papers">Forthcoming</a></li>
	  <li><a href="allvols.cgi?journal=P" title="View all published volumes">All&nbsp;volumes</a></li>
	  <li><a href="index.html" title="Go to Perception homepage">Perception&nbsp;homepage</a></li>
          <li><a href="ECVP.html" title="ECVP abstracts">ECVP</a></li>
	  <li><a href="http://www.pion.co.uk" title="Go to Pion ltd homepage">Pion&nbsp;homepage</a></li>
	</ul>
      </div>
    </div>
    <div id="title">
      <font size=4>
	<div class="left">Email alerting service registration</div>
	<div class="center"></div>
	<div class="right"></div>
      </font>
    </div>


END
} elsif($journal eq 'X'| $journal eq 'E'| $journal eq 'A'| $journal eq 'B'| $journal eq 'C'| $journal eq 'D') {
 print <<END;
    <div id="header">
      <a href="$journal.html"><img src="Images/$bannername{$journal}" alt="$jname{$journal}" class="logo" /></a>
      <a href="http://www.pion.co.uk"><img src="Images/right_ban.gif" alt="Pion Ltd" class="pionlogo" /></a>
    </div>
    <div id="total">
      <div id="top-buttons">
	<div class="topnavigation">
	  <ul>
	    <li><a href="A.html" title="Go to Environment and Planning A homepage">EPA&nbsp;homepage</a></li>
	    <li><a href="B.html" title="Go to Environment and Planning B homepage">EPB&nbsp;homepage</a></li>
	    <li><a href="C.html" title="Go to Environment and Planning C homepage">EPC&nbsp;homepage</a></li>
	    <li><a href="D.html" title="Go to Environment and Planning D homepage">EPD&nbsp;homepage</a></li>
	    <li><a href="index.html" title="Go to Environment and Planning homepage">EP&nbsp;homepage</a></li>
	    <li><a href="http://www.pion.co.uk" title="Go to Pion ltd homepage">Pion&nbsp;homepage</a></li>
	  </ul>
	</div>
      </div>
      <div id="title">
      <font size=4>
	<div class="left">Email alerting service registration</div>
	<div class="center"></div>
	<div class="right"></div>
      </font>
    </div>

END
} else {
 print <<END;
   <div id="header">
      <a href="http://www.pion.co.uk"><img src="Images/pion_new2.gif" alt="Pion" class="logo"/></a>
      <a href="http://www.pion.co.uk"><img src="Images/right_ban.gif" alt="" class="pionlogo" /></a>
    </div>
    <div id="total">
      <div id="top-buttons">
	<div class="topnavigation">
	  <ul>
	    <li><a href="librarians.html" title="Information for librarians">For&nbsp;librarians</a></li>
	    <li><a href="contacts.html" title="Contact Pion">Pion&nbsp;contacts</a></li>
	    <li><a href="index.html" title="Go to Pion ltd homepage">Pion&nbsp;homepage</a></li>
	  </ul>
	</div>
      </div>
      <div id="title">
      <font size=4>
	<div class="left">Email alerting service registration</div>
	<div class="center"></div>
	<div class="right"></div>
      </font>
    </div>
END
}

$footer=<<END;
       <div class="space"></div>
    <div id="footer">
	<div class="right">Copyright &copy; $thisyear a <a href="http://www.pion.co.uk">Pion</a> publication.</div>
    </div>
END

if ($email eq $emailconf && $email=~/.+@.+?\.\w+$/ && $valid_captcha){
  #
  #print p, "[addresses match and have the right form, valid captcha]";
  
  $mail = new Mail::SendEasy(smtp => 'mailgate.pion.ltd.uk');
  
  #$email='jon@pion.co.uk'; #override real email for testing purposes

  # generate random number $random, get next id from db, insert all into database 

  
  # check if already subscribed
  $sth=$db->prepare("select id, random from emailaddresses where email='$email' and journal='$journal' and confirmed is true;");
  $sth->execute();
  ($old_id, $old_random)=$sth->fetchrow();
  
  if ($old_id){
    print p, "You are already subscribed to email alerting for $jname{$journal}. You will receive an email alert when new papers are added to the <i>$jname{$journal}</i> website, or, in rare cases, when we need to convey important information concerning the journal or website. No further action is required. <p> Click <a href='$journal.html'>here</a> to go to the journal homepage. <p>If you wish to unsubscribe from the alerting service, please click <a href='unsubscribe.cgi?i=$old_id&amp;n=$old_random'>here</a>.", $footer, end_html;
    exit;
  }
  
  $sth=$db->prepare("select count(*) from emailaddresses where email='$email' and journal='$journal' and confirmed is false and now()-regdate<'3 minutes';");
  $sth->execute();
  ($registered)=$sth->fetchrow(); 
  
  if ($registered>0){
    print p, "You have already registered for email alerting to $jname{$journal}, and an activation email was sent to your address. Please click the link in the email we sent to activate the alerting service. If you do not recall receiving the activation email, please check carefully if the message has been identified as spam by your spam filters. If the activation email was identified as spam, please ensure that any spam filtering on your system is set to accept email from pion.co.uk, so that the notification emails will not also be identified as spam. <p>Click <a href='$journal.html'>here</a> to go to the $jname{$journal} homepage.", $footer, end_html;
    exit;
  }
  
  $sth=$db->prepare("select nextval('id_seq')");
  $sth->execute();
  ($id)=$sth->fetchrow();
  
  $random=int(rand(1000000));
  
  $email_q=$db->quote($email);

   
  $db->do("insert into emailaddresses values ($id, $email_q, '$journal', $random, now(), false)"); 
  #print "insert into emailaddresses values ($id, $email_q, '$journal', $random, now, false)" ;
  $status = $mail->send(
         from    => 'alerts@pion.co.uk' ,
         from_title => 'Pion email alerting service',
         to      => $email ,
         subject => "$jname{$journal} email alerting activation" ,
         msg     => "Thank you for signing up to the email alerting service for $jname{$journal}.\n\nIn order to activate the service, please click on the following link:\n\nhttp://$baseurl{$journal}/emailconfirm.cgi?i=$id&n=$random\n\nYou will be able to unsubscribe at any point simply by clicking on the \"unsubscribe\" link which can be found in the alert emails.\n\n\nPlease do not reply to this message.\n"
         )  ;
         print "Problem sending message" if($mail->error); 
  print p, "An email message has now been sent to your address. Please open the message and click on the link to activate the email alerting service for <i>$jname{$journal}</i>. If you have not received this message within three minutes please check if the message has been identified as spam by your spam filters. If the activation email was identified as spam, please ensure that any spam filtering on your system is set to accept email from pion.co.uk, so that the notification emails will not also be identified as spam.
<p> Click <a href='$journal.html'>here</a> to go to the journal homepage.", $footer, end_html;
  
  
}

else {
  $errormsg="<font color='red'>The email addresses entered do not match or are invalid. </font>" unless $email eq $emailconf;
  $errormsg .= "<font color='red'><br>The verification words were not recognised - please try again.</font>" unless $valid_captcha || !$email;
  printform($errormsg);

}

sub printform {
  #if ($host !~ /envplan.com$/ && $host !~ /perceptionweb.com$/ && $host !~ /hthpweb.com$/){
   # print p, "The registration page you are trying to access will not operate correctly via a proxy address, which you appear to be using (for example, you might have accessed the $baseurl{$journal} pages via a university login). In order to register for email alerts, please copy and paste the following address into your web browser and complete the instructions therein: <p>http://$baseurl{$journal}/alertregister.cgi?journal=$journal <p>Once you have completed the registration process, you can continue to access $baseurl{$journal} pages via your proxy address."
  #} 
  #else {
     $captcha_blurb='and enter the two security words into the dialog box provided. (Note: the security words are not case sensistive, and a facility exists to generate new words if the those currently displayed are difficult to read; an audio security feature is also available, for the visually impaired. These features are accessed via the red buttons to the right of the dialog box)' unless $TESTMODE;
    print "<p>If you would like to receive email alerts whenever new papers are uploaded to the <i>$jname{$journal}</i> site (including advance online publications), please enter and confirm your email address in the boxes provided below$captcha_blurb. 
  <p>Your email will not be divulged to any third parties and will only be used to send alerts of new papers, and, in rare cases, to alert you of major changes to the journal or website. You can unsubscribe at any point by clicking on the link provided in the alert emails.<br>";
    if ($journal eq 'X'| $journal eq 'E'| $journal eq 'A'| $journal eq 'B'| $journal eq 'C'| $journal eq 'D') {
      print "<p>Please note that an identical service is offered by each of the <i>Environment and Planning</i> journals; to subscribe to the alerting service for another <i>E&P</i> journal please visit the journal homepage from the links above.<br>";
    }
    print  $_[0], p,
      start_form, "Enter email address: <br>", textfield(-name=>'email', -size=>50),
      br, "Confirm email address: <br>", textfield(-name=>'emailconf', -size=>50), "<input type=hidden name = journal value =$journal>", br
      br, $captcha, br, p, "<b>Note: Before clicking Submit, please ensure that any spam filtering on your system is set to accept email from pion.co.uk.</b>",
      p, submit(-name=>'Submit'), end_form, $footer, end_html;
   #} 
    exit;
}
