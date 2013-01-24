#!/bin/perl
use CGI::Pretty qw/:standard/;
use Mail::SendEasy;

$email=param('email');
$email2=param('email2');
$message=param('message');
$to=param('to');
$subject=param('subject');
$name=param('name');
$inst=param('inst');
$journ=param('journ');
$refer=param('refer');  


              
 @weekDays = qw(Sun Mon Tue Wed Thu Fri Sat Sun);
($second, $minute, $hour, $dayOfMonth, $month, $yearOffset, $dayOfWeek, $dayOfYear, $daylightSavings) = localtime();
$thisyear = 1900 + $yearOffset;
$month++;                   

print header;
#default_dtd('-//W3C//DTD HTML 4.0 Transitional//EN');
print start_html(-style=>"pion.css", -title=>$jname{$journal}."Online registration", -script=>$jscript, -id=>$jid{$journal}, -head=>Link({-rel=>'alternate', -title=>'Pion RSS feed', -href=>"rss.cgi?journal=$journal", -type=>'application/rss+xml'}), -dtd=>'-//W3C//DTD HTML 4.0 Transitional//EN');
#print start_html(-title=>'Contact Pion', -style=>'pion.css');
     

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

 print <<END;
      <div class="space"></div>
      <p>Institutional subscribers (and personal subscribers with a static IP address) are entitled to free access to the online full-text articles, provided they have a subscription to the corresponding volume. If your institution has a current print subscription and you are unable to access the current volume online, please ask your librarian (or person responsible for journal subscriptions) to complete this form. Access to earlier online volumes, where available, requires subscription to the corresponding print volume. <b>Please note that we cannot accept applications from anyone other than a librarian or authorised administrator</b>.</p>
	
      <p>Please complete this form as thoroughly as possible. In particular, please include details of your <b>organisation</b>, <b>subscription agent</b> (if you have one), <b>order number</b>, and <b>contact details</b>. Please note that, in order to identify you unambiguously on our system, we require you to enter your <b>customer identification number</b>, if known. You will find this 3 or 4 digit number on your address label. If you are unable to do this, please ensure that you have at least entered an order number. (These numbers are important because, unless we can identify your subscription record, we will not be able to register your IP addresses. In some cases we might not have a record of end-user addresses, and so your address alone may not be sufficient to identify you on our system.)</p> 
	
      <p><b>Renewals.</b> Please note that it is not necessary to complete this form each time you renew or if you subscribe to additional journals or volumes. If you have previously registered, only complete this form if you have any changes of details.</p>
	
      <p>Unfortunately, this service is not currently available as a separate electronic-only subscription.</p>
      <FORM ACTION="/cgi-bin/pion/e-pion-register.pl" METHOD=POST>
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
	  <DT>Zip/Postal code:
	  <DD><INPUT TYPE=text NAME="zip" MAXLENGTH=30><BR>
	  <DT>Country:
	  <DD><INPUT TYPE=text NAME="country" MAXLENGTH=30><BR>
	  <DT>E-mail address:
	  <DD><INPUT TYPE=text NAME="email" MAXLENGTH=45><BR>
          <DT>Journals subscribed to: 
          <DD><SELECT NAME="journal">
	      <OPTION VALUE="ep" SELECTED>Environment and Planning (A, B, C, D, or combinations thereof)<OPTION VALUE="perception">Perception<OPTION VALUE="perception + ep">Perception + one or more Environment and Planning journals</SELECT>&nbsp;<BR>	  
          <DT>Customer number (see address label) - please enter if possible:
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
      <div class="right">Copyright &copy; $thisyear Pion Ltd.</div>
    </div>
      </div>
END
#================================================
      print end_html; 


#print form, including any error message, and exit
sub printform {
  print h1("Contact <i>$to</i> at Pion") unless $journ;
  
  #print $ENV{'HTTP_REFERER'};
  
  print p,"<font color='red'>Error: $_[0]</font>",p if $_[0];
  
  print <<END;
     <div class="space"></div>
<form action="contact.cgi" method="post">
<input type="hidden" name="to" value="$to"><input type="hidden" name="refer" value="$ENV{'HTTP_REFERER'}">
Please enter your name:<br>
<input type="text" name="name" value="$name"><br>
Institution (if applicable):<br>
<input type="text" name="inst" value="$inst"><br>
Email address (please enter this carefully as we will need it to reply to you):<br>
<input type="text" name="email"><br>
Please enter your email address again for confirmation:<br>
<input type="text" name="email2">
<p>Subject:<br>
<input type="text" name="subject" size=80 value="$subject">
<p>Message:
<br><textarea name="message" cols="80" rows="16" size="5000">$message</textarea>
<p><input type="submit" value="Send message">
</form>
    <div class="space"></div>
    <div id="footer">
      <div class="right">Copyright &copy; $thisyear a <a href="http://www.pion.co.uk">Pion</a> publication.</div>
    </div>
END
  print end_html;
  exit;
}
