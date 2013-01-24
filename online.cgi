#!/bin/perl
use CGI::Pretty qw/:standard/;
use Mail::SendEasy;
#use Captcha::reCAPTCHA;

#my $c = Captcha::reCAPTCHA->new;


$to			='sales'; # All emails to go to sales
$subject		=param('Online registration form');

#New calls for email
$title		=param('title');
$name1		=param('name1');
$name2		=param('name2');
$position	=param('position');
$department 	=param('department');
$inst		=param('org');
$address1 	=param('address1');
$address2 	=param('address2');
$address3 	=param('address3');
$zip 		=param('zip');
$country 	=param('country');
$email		=param('email');
$email2		=param('email2');
$journal	=param('journal');
$client 	=param('client');
$agent 		=param('agent');
$ordnum 	=param('ordnum');
$allow 		=param('allow');
$deny 		=param('deny');
#Previous calls
$journ		=param('journ');
$refer		=param('refer');  


#$challenge=param('recaptcha_challenge_field');
#$response=param('recaptcha_response_field');
                 

print header;
#default_dtd('-//W3C//DTD HTML 4.0 Transitional//EN');
print start_html(-style=>"pion.css", -title=>$jname{$journal}."Online registration", -script=>$jscript, -id=>$jid{$journal}, -head=>Link({-rel=>'alternate', -title=>'Pion RSS feed', -href=>"rss.cgi?journal=$journal", -type=>'application/rss+xml'}), -dtd=>'-//W3C//DTD HTML 4.0 Transitional//EN');
#print start_html(-title=>'Contact Pion', -style=>'pion.css');

#Destination
%destination=('sales','online@pion.co.uk') ;

#============= Print journal specific stuff ===========
if($journ eq 'P'){
 print <<END;
<div id="header">
    <a href="index.html"><img src="Images/p_ban2.gif" alt="Perception" class="logo" /></a>

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
	  <li><a href="http://www.pion.co.uk" title="Go to Pion ltd homepage">Pion&nbsp;homepage</a></li>
	</ul>
      </div>
    </div>
      <div id="title">
	<font size=4>
	  <div class="left">Application form for full-text access to <i>Perception</i> articles</div>
	  <div class="center"></div>
	  <div class="right"></div>
	</font>
      </div>
END
} elsif($journ eq 'X'| $journ eq 'E'| $journ eq 'A'| $journ eq 'B'| $journ eq 'C'| $journ eq 'D') {
 print <<END;
    <div id="header">
      <a href="index.html"><img src="Images/ep_ban.gif" alt="environment and planning" class="logo" /></a>
      <a href="http://www.pion.co.uk"><img src="Images/right_ban.gif" alt="Pion Ltd" class="pionlogo" /></a>
    </div>
    <div id="total">
      <div id="top-buttons">
	<div class="topnavigation">
	  <ul>
	    <li><a href="search.cgi" title="Search abstracts">Search</a></li>
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
	  <div class="left">Application form for full-text access to <i>Environment and Planning</i> articles</div>
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
	  <div class="left">Application form for full-text access to articles published by Pion Ltd</div>
	  <div class="center"></div>
	  <div class="right"></div>
	</font>
      </div>
END
}

#================================================

#======= print common html stuff ================
###################################################
# Need to make this a link to a general form, rather than journal specific. COuld add a field listing journal subscribed to. Also want this page to be a pop-up with Pion version, not individual versions for each journal #
#PRINT if email is empty 
unless ($email){
 print <<END;
      <div class="space"></div>
      <p>Institutional subscribers (and personal subscribers with a static IP address) are entitled to free access to the online full-text articles, provided they have a subscription to the corresponding volume. If your institution has a current print subscription and you are unable to access the current volume online, please ask your librarian (or person responsible for journal subscriptions) to complete this form. Access to earlier online volumes, where available, requires subscription to the corresponding print volume. <b>Please note that we cannot accept applications from anyone other than a librarian or authorised administrator</b>.</p>
	
      <p>Please complete this form as thoroughly as possible. In particular, please include details of your <b>organisation</b>, <b>subscription agent</b> (if you have one), <b>order number</b>, and <b>contact details</b>. Please note that, in order to identify you unambiguously on our system, we require you to enter your <b>customer identification number</b>, if known. You will find this 3 or 4 digit number on your address label. If you are unable to do this, please ensure that you have at least entered an order number. (These numbers are important because, unless we can identify your subscription record, we will not be able to register your IP addresses. In some cases we might not have a record of end-user addresses, and so your address alone may not be sufficient to identify you on our system.)</p> 
	
      <p><b>Renewals.</b> Please note that it is not necessary to complete this form each time you renew or if you subscribe to additional journals or volumes. If you have previously registered, complete this form only if you have any changes of details.</p>
	
      <FORM ACTION="online.cgi" METHOD=POST>
	<BR>

<DL COMPACT>
	<DT>Title: <SELECT NAME="title">
	      <OPTION VALUE="Mr" SELECTED>Mr<OPTION VALUE="Mrs">Mrs<OPTION VALUE="Ms">Ms<OPTION VALUE="Miss">Miss<OPTION VALUE="Dr">Dr<OPTION VALUE="Prof">Prof</SELECT>
	  <DT>First name:
	  <DD><INPUT TYPE=text NAME="name1" SIZE="30">&nbsp;
	  <DT>Last name:
	  <DD><INPUT NAME="name2" SIZE="30"><BR>
	  <DT>Job title:
	  <DD><INPUT TYPE=text NAME="position" MAXLENGTH=30><BR>
	  <DT>Department:
	  <DD><INPUT TYPE=text NAME="department" MAXLENGTH=30><BR>
	  <DT>Organisation:
	  <DD><INPUT TYPE=text NAME="org" MAXLENGTH=30><BR>
	  <DT>Address:
	  <DD><INPUT TYPE=text NAME="address1" MAXLENGTH=30><BR>
	  <DT>
	  <DD><INPUT TYPE=text NAME="address2" MAXLENGTH=30><BR>
	  <DT>
	  <DD><INPUT TYPE=text NAME="address3" MAXLENGTH=30><BR>
	  <DT>Zip/postal code:
	  <DD><INPUT TYPE=text NAME="zip" MAXLENGTH=30><BR>
	  <DT>Country:
	  <DD><INPUT TYPE=text NAME="country" MAXLENGTH=30><BR>
	  <DT>E-mail address:
	  <DD><INPUT TYPE=text NAME="email"   MAXLENGTH=45><BR>
	  <DT>Confirm e-mail address:
	  <DD><INPUT TYPE=text NAME="email2" MAXLENGTH=45><BR>
          <DT>Journals subscribed to: 
          <DD><SELECT NAME="journal">
	  <OPTION VALUE="ep" SELECTED>Environment and Planning (A, B, C, D, or combinations thereof)<OPTION VALUE="perception">Perception<OPTION VALUE="perception + ep">Perception + one or more Environment and Planning journals</SELECT>&nbsp;<BR>	  
          <DT>Customer number (see address label)&mdash;please enter if possible:
	  <DD><INPUT TYPE=text NAME="client" MAXLENGTH=30><BR>
	  <DT>Name of subscription agent (if applicable):
	  <DD><INPUT TYPE=text NAME="agent" MAXLENGTH=30><BR>
	  <DT>Order number (of agent, if applicable, otherwise organisation's). Please ensure that you enter a valid order number if you do not know your customer number: <DD><INPUT TYPE=text NAME="ordnum" MAXLENGTH=30><BR>
	  <DT>IP addresses of subnets to be allowed access (in the form xxx.yyy.zzz or xxx.yyy, eg 192.123.111 or 192.123): <DD><TEXTAREA NAME="allow" COLS=30 ROWS=4></TEXTAREA><BR>
	  <DT>IP addresses to be <B>denied</B> access (eg unrestricted proxy servers): <DD><TEXTAREA NAME="deny" COLS=30 ROWS=2></TEXTAREA>
	</DL>
	Please note that all computers to be given access must be located within the organisation. Any proxy servers on an authorised network must be configured to reject forwarding requests from nonauthorised networks. If this is not the case, please enter their IP addresses above so that they can be denied access to full-text articles.
	
	<BR><BR><B>Submission of this form implies acceptance of above conditions and the <a href="pion-online-licence.html">Pion licence agreement</a></B>.<BR><BR>
	<INPUT TYPE=submit VALUE="Submit form and register for online access">
      </FORM>
    <div class="space"></div>
    <div id="footer">
      <div class="right">Copyright Pion Ltd.</div>
    </div>
      </div>
END
}

else
{
#Submission

if( ($email=~/^[a-zA-Z][\w\.-]*[a-zA-Z0-9]@[a-zA-Z0-9][\w\.-]*[a-zA-Z0-9]\.[a-zA-Z][a-zA-Z\.]*[a-zA-Z]$/ && $email eq $email2) && $email && $name1){
 #print "email ok";
 if ($destination{$to}){
  #send email     
  $mail = new Mail::SendEasy(smtp => 'mailgate.pion.ltd.uk');
  $status = $mail->send(
  from    => $email ,
  from_title => $name1 ,
  to      => $destination{$to} ,
  subject => "[Online Registration $inst]$subject " ,
  msg     => "
[Sent via Pion Online Registration]\n
To: $to\n
From: $name1 <$email>\n
========>\n
	Title		: $title\n
	Name1		: $name1\n
	Name2		: $name2\n
	Position	: $position\n
	Department 	: $department\n
	Inst		: $inst\n
	Address1 	: $address1\n
	Address2 	: $address2\n
	Address3 	: $address3\n
	Zip 		: $zip\n
	Country 	: $country\n
	Email		: $email\n
	Journal		: $journal\n
	Client 		: $client\n
	Agent 		: $agent\n
	Ordnum 		: $ordnum\n
\n
Allow IP		: \n
========>\n
$allow\n
\n
Deny IP	 	:    
========>\n  
$deny\n 
=====END===\n"
         )  ;

  if($mail->error){
   print h1('Problem sending message'), p, "We regret that a technical problem has prevented your message being sent, please send your message directly to $destination{$to}"
  }
  else {
   print h1('Message sent'), p, 'Thank you for your message';
   print p, "<a href='$refer'>Continue</a>"  if $refer;
  }
 }
}

#Email mismatch
else {
 print h1('Problem with message'), p, 'The email address did not match or you did not put a name. Please try again.';
}

#End of: Submission
}

#================================================
      print end_html; 

