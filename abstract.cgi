#!/usr/bin/perl 
# CGI script to tesp IP. 
# Usage: .../abstract.cgi?id=p1234
# Alternative: ..../abstract.cgi?journal=A&volume=30&page=124

# TODO: deny access to full text <1999 unless archive subscribed to

#Functional testing of ip address if set to 1; rfc Sep '11
#RFC: Dec '12 Added test to check for year+1 incase of new subs added at end of year not triggereing the back arcive
$FUNKYTEST=0;

use DBI;
use CGI qw(:standard -no_xhtml);
require('getuid.pl');

@weekDays = qw(Sun Mon Tue Wed Thu Fri Sat Sun);
($second, $minute, $hour, $dayOfMonth, $month, $yearOffset, $dayOfWeek, $dayOfYear, $daylightSavings) = localtime();
$thisyear = 1900 + $yearOffset;
$month++;

$id=secure(param('id'));
$journal=secure(param('journal'));
$volume=secure(param('volume'));
$page=secure(param('page'));
$pw=secure(param('pw'));
$diagnostic=secure(param('diagnostic'));
$FALSEIP=param('falseip');

$pw_string='&amp;pw=1' if $pw==1;

%jname= (
 "V" => "Perception ECVP Abstract Supplement",
 "P" => "Perception",
 "H" => "High Temperatures - High Pressures",
 "A" => "Environment and Planning A",
 "B" => "Environment and Planning B: Planning and Design",
 "C" => "Environment and Planning C: Government and Policy",
 "D" => "Environment and Planning D: Society and Space"
);

%journalpage=(
 "H" => "HTHP",
 "P" => "Perception",
 "A" => "EPA",
 "B" => "EPB",
 "C" => "EPC",
 "D" => "EPD"
);  

%lower=(
 "H" => "h",
 "P" => "p",
 "A" => "a",
 "B" => "b",
 "C" => "c",
 "D" => "d"
);

%jid=(
 "H" => "hthp",
 "P" => "per",
 "A" => "epa",
 "B" => "epb",
 "C" => "epc",
 "D" => "epd"
);

%issn=(
 "H" => "0018-1544",
 "P" => "0301-0066",
 "A" => "0308-518X",
 "B" => "0265-8135",
 "C" => "0263-774X",
 "D" => "0263-7758"
);  

%eissn=(
 "H" => "",
 "P" => "1468-4233",
 "A" => "1472-3409",
 "B" => "1472-3417",
 "C" => "1472-3425",
 "D" => "1472-3433"
);  

%pdfpath= (
 "H" => "hthp/fulltext/h",
 "P" => "perception/fulltext/p",
 "A" => "epa/fulltext/a",
 "B" => "epb/fulltext/b",
 "C" => "epc/fulltext/c",
 "D" => "epd/fulltext/d"
);

%refpath=(
 "H" => "hthp/abstracts/h",
 "P" => "perception/abstracts/p",
 "A" => "epa/abstracts/a",
 "B" => "epb/abstracts/b",
 "C" => "epc/abstracts/c",
 "D" => "epd/abstracts/d"  
);

%edpdfpath = (
 "H" => "hthp/editorials",
 "P" => "perception/editorials",
 "A" => "epa/editorials",
 "B" => "epb/editorials",
 "C" => "epc/editorials",
 "D" => "epd/editorials"
);


if ($journal eq 'A' or $id=~/^a/){$header="Environment and Planning A abstract"}
elsif ($journal eq 'B' or $id=~/^b/){$header="Environment and Planning B abstract"}
elsif ($journal eq 'C' or $id=~/^c/){$header="Environment and Planning C abstract"}
elsif ($journal eq 'D' or $id=~/^d/){$header="Environment and Planning D abstract"}
elsif ($journal eq 'H' or $id=~/^h/){$header="HTHP abstract"}
elsif ($journal eq 'P' or $id=~/^p/){$header="Perception abstract"}
elsif ($journal eq 'V' or $id=~/^v/){$header="Perception ECVP abstract"}


$jscript= <<END;


var newwindow;
function popitup(url) {
	newwindow=window.open(url,'SFXmenu','location=no, status=yes, menubar=no, scrollbars=yes, resizable=yes, width=460');
	if (window.focus) {newwindow.focus()}
	return false;
}

function popitup2(url) {
	newwindow=window.open(url,'ftext','location=no, status=yes, menubar=no, scrollbars=yes, resizable=yes');
	if (window.focus) {newwindow.focus()}
	return false;
}
END

print header(-type=>'text/html', -charset=>'utf-8', -expires=>'600');
my @fieldnames = param();



$dbh = DBI->connect("dbi:Pg:dbname=journals;host=localhost;port=5432", "jon", "")||die "couldn't connect";


if($id)
{
   $sth=$dbh->prepare("
   SELECT papers.year, papers.journal, papers.title, papers.volume, papers.issue, papers.abstract, papers.received,  papers.start_page, papers.end_page, papers.page_prefix, papers.paperid, papers.ptype, papers.misc, papers.same_as, virtual_themes.openaccess, papers.open_access
   FROM papers 
   LEFT JOIN virtual_themes
    ON papers.virtual_theme = virtual_themes.virtual_theme_id
   WHERE papers.paperid='$id';
") || die;
}
else 
{
   $sth=$dbh->prepare("
SELECT papers.year, papers.journal, papers.title, papers.volume, papers.issue, papers.abstract, papers.received,  papers.start_page, papers.end_page, papers.page_prefix, papers.paperid, papers.ptype, papers.misc, papers.same_as, virtual_themes.openaccess, papers.open_access
   FROM papers 
   LEFT JOIN virtual_themes
    ON papers.virtual_theme = virtual_themes.virtual_theme_id
WHERE papers.journal='$journal' and papers.volume=$volume and papers.start_page=$page;
")||die;
}

$sth->execute()||die "Can't execute query\n";
@result=$sth->fetchrow();

#Rfc Apr 2012: $openaccess Virtual issue OO, $paper_open: A paper is open access
if (@result==0){print "<p>No matching abstract $id</p><a href='/'>Go to homepage</a>"}
else{
  ($year, $journal, $title, $volume, $issue, $abstract, $received, $start_page, $end_page, $page_prefix, $paperid, $ptype, $misc, $same_as, $openaccess, $paper_open)=@result;

  if($journal eq 'A' && $volume < 6 && $volume>0){$journalname='Environment and Planning'}
  elsif($journal eq 'B' && $volume < 10 && $volume>0){$journalname='Environment and Planning B'}
  else {$journalname=$jname{"$journal"}}  
  

 if ($journal eq 'H') { # Take care of anomalous years in HTHP volumes
  if ($volume==27) { 
    $xvolume="27/28";
    $xyear="1995/1996";
  } elsif ($volume==35) {
    $xvolume="35/36";
    $xyear="2003/2007";
  } else {
    $xvolume=$volume;
    $xyear=$year;
  }
}

  print start_html(-style=>"pion.css", -title=>$header, -script=>$jscript, -id=>$jid{$journal}, -dtd=>'-//W3C//DTD HTML 4.0 Transitional//EN');
    
  $paperid=~s/ $//;
  $issuestring=$issue;
  $issuestring="supplement" if $ptype==9;
  if ($ptype==11){
    $heading="Books received"
  } 
  elsif ($journal eq 'V'){ 
    $heading="ECVP $year Abstract"
  }
  elsif ($start_page==0){
   $heading="Advance online publication";
  }
  elsif ($journal eq 'H') {
    $heading="<b>$xyear</b> volume <a href='contents.cgi?journal=$journal&amp;volume=$volume$pw_string'><b>$xvolume</b></a>(<a href='contents.cgi?journal=$journal&amp;volume=$volume&amp;issue=$issue$pw_string'>$issue</a>) $pagerange";
  } else { if($start_page==$end_page){
      $pagerange="page $page_prefix$start_page"
    }
    else
    {
      $pagerange="pages $page_prefix$start_page&nbsp;&#8211;&nbsp;$page_prefix$end_page";
    }
     $lb='';$rb='';
     if($issue>0){$lb='(';$rb=')'}
    $heading="<b>$year</b> volume <a href='contents.cgi?journal=$journal&amp;volume=$volume$pw_string'><b>$volume</b></a>$lb<a href='contents.cgi?journal=$journal&amp;volume=$volume&amp;issue=$issue$pw_string'>$issue</a>$rb $pagerange";
  }
    $gif=lc($journal).'_ban.gif';
    $banner="<img src=\"Images/$gif\" alt=\"$jname{$journal}\" border=0 class=\"logo\">" if $journal=~/(A|B|C|D)/;

    #$banner='<img src="Images/ep_left_ban.gif" alt="environment and planning" border=0 class="logo">' if $journal=~/(A|B|C|D)/;
    $banner='<img src="Images/p_ban2.gif" alt="Perception" border=0 class="logo">' if $journal=~/(P|V)/;

    $banner='<img src="Images/h_ban2.gif" alt="High Temperatures - High Pressures" border=0 class="logo">' if $journal=~/(H)/;
    
    $j_name=$jname{$journal};

    if ($ptype==0 || $ptype==1 || $ptype==2 || $ptype==3 || $ptype==5 || $ptype==9 or $ptype==11 or $journal eq 'V') { $doi="doi:10.1068/$paperid"; }
    
    $button2="<li><a href=\"index.html\" title=\"View EP homepage\">EP&nbsp;homepage</a></li>" unless ($journal eq 'P' or $journal eq 'V' or $journal eq 'H');
    $button2="<li><a href=\"ECVP.html\" title=\"ECVP abstracts\">ECVP</a></li>" if ($journal eq 'P' or $journal eq 'V');
    $button2="<li><a href=\"$journal.html\" title=\"View $j_name homepage\">$journalpage{$journal}&nbsp;homepage</a></li>" if ($journal eq 'H');

    $searchjournal=$journal;
    if ($journal eq 'V'){$journal='P'; $ecvp=1}
    print <<END;
      <div id="header">
      <a href="$journal.html">$banner</a>
      <a href="http://www.pion.co.uk"><img src="Images/right_ban.gif" alt="Pion Ltd" class="pionlogo" /></a>
    </div>
    <div id="total">
      <div id="top-buttons">
	<div class="topnavigation">
	  <ul>
	    <li><a href="search.cgi?journal=$searchjournal$pw_string" title="Search all papers">Search</a></li>
END
unless ($journal eq 'H') {
  print "	    <li><a href=\"contents.cgi?journal=$journal&amp;issue=current$pw_string\" title=\"View latest issue\">Current&nbsp;issue</a></li>";
  print "	    <li><a href=\"contents.cgi?journal=$journal&amp;volume=forthcoming$pw_string\" title=\"View advance online publications\">Forthcoming</a></li>";
  print "           <li><a href=\"allvols.cgi?journal=$journal$pw_string\" title=\"View all published volumes\">All&nbsp;volumes</a></li>";
  print "	    <li><a href=\"$journal.html\" title=\"View $j_name homepage\">$journalpage{$journal}&nbsp;homepage</a></li>";
} else {
  print "           <li><a href=\"allvols_h.html\" title=\"View pre-2008 volumes\">Pre-2008 volumes</a></li>";
}
print <<END;
            $button2
	  <li><a href="http://www.pion.co.uk" title="Go to Pion ltd homepage">Pion&nbsp;homepage</a></li>
	  </ul>
	</div>
      </div>
      <div id="title">	
	<div class="left"><font size=4>$heading</font></div>
	<div class="center"></div>
	<div class="right"><font size=4>$doi</font></div>	
      </div>

END







# confound incorrect links from Google Scholar
# TODO:  enable redirection
#($ENV{'HTTP_HOST'} ne 'www.perceptionweb.com' && $ENV{'HTTP_HOST'} ne 'perceptionweb.com' && $ENV{'HTTP_HOST'} ne 'perceptionweb.co.uk' && $ENV{'HTTP_HOST'} ne 'proton4') && $journal eq 'P'
if(($ENV{'HTTP_HOST'} !~ /perceptionweb/ && $ENV{'HTTP_HOST'} ne 'proton5'&& $ENV{'HTTP_HOST'} ne 'gate.pion.ltd.uk:8732') && $journal eq 'P'){
  print p, "Incorrect url<p><a href='http://www.perceptionweb.com/abstract.cgi?id=$paperid'>Please click here.</a>\n", end_html;
  exit;
}
if(($ENV{'HTTP_HOST'} ne 'gate.pion.ltd.uk:8732' && $ENV{'HTTP_HOST'} ne 'www.envplan.com' && $ENV{'HTTP_HOST'} ne 'envplan.com' && $ENV{'HTTP_HOST'} ne 'envplan.co.uk' && $ENV{'HTTP_HOST'} ne 'proton5') && ($journal eq 'A' || $journal eq 'B' || $journal eq 'C' || $journal eq 'D')){
  print p, "Incorrect url<p><a href='http://www.envplan.com/abstract.cgi?id=$paperid'>Please click here.</a>\n", end_html;
  exit;
}
   
  # print p, "<b>We regret that this page does not currently display correctly in Internet Explorer 7.0.  We intend to correct this as quickly as possible, but in the meantime please use a previous version or <a href='http://getfirefox.com'>Firefox</a>.</b>" if $ENV{'HTTP_USER_AGENT'} =~ /MSIE 7\.0/;
 
   # print "<i>$journalname</i> $year volume <a href='contents.cgi?journal=$journal&volume=$volume$pw_string'><b>$volume</b></a>(<a href='contents.cgi?journal=$journal&volume=$volume&issue=$issue$pw_string'>$issuestring</a>) $page_prefix$start_page&#8211;$page_prefix$end_page\n";
  #}

  $authquery=$dbh->prepare("select first_name, last_name, suffix from authors where paperid='$paperid' order by position")||die;
  $authquery->execute()||die;
  while (@author=$authquery->fetchrow()){
    ($first_name,$last_name,$suffix)=@author;
    
    $suffix="&nbsp;$suffix" if $suffix;
    
    $authorline .=  "$first_name&nbsp;$last_name$suffix, ";
    if ($first_name =~ s/\s(del|van der|van de|von der|von|van den|van|de)\b//i){
      $vans_etc="$1&nbsp;"}
    else
      {$vans_etc=""}
    
    $openurl_author_surname="$vans_etc$last_name" unless $openurl_author_surname;
    #$openurl_author_fname=$first_name unless $openurl_author_fname;
      
    $initials='';  
    @fnames=split(/ /, $first_name);
    for $fn (@fnames){
      unless($fn=~/-/){
        $fn =~ /(\w|&.*?;).*?/; 
        $initials .= "$1 ";
      } else {
        $fn =~ /(\w|&.*?;).*?-(\w|&.*?;)/;
        $initials .= "$1-$2 ";
      }
    }
    #$first_name =~ /(\w|&.*?;).*?\b/;

    #print "first name: $1"; 
    
    #$first_name=$1;
    #$first_name =~ s/ $//;
     $initials =~ s/ $//;
    
    $openurl_author_initials=$initials unless $openurl_author_initials;
    $openurl_author_initials =~ s/ //g;
    
    $authorline2 .= "$vans_etc$last_name&nbsp;$initials$suffix, ";    
  }
  $authorline =~ s/, $//;
  $authorline2 =~ s/, $//;
  # $authorline2 =~ s/^(.*?),.*?,.*/$1 et al/;  # 3 or more authors
  # $authorline2 =~ s/, / and /; # 2 authors
 
  # print citation information 
  print '<p class=ref><font size=-1>Cite as:',br if (($ptype==0||$ptype==1||$ptype==2||$ptype==5||$ptype==8||$ptype==9||$ptype==10||$ptype==16||$ptype==13||$ptype==14||$ptype==15)&&$authorline2);
  if ($ecvp){
    $yearstr="$year, ";
    $ecvp_page=",&nbsp;page&nbsp;$start_page" if $start_page;
    print  "$authorline2, $yearstr\"$title\" <i>Perception</i> <b>$volume</b> ECVP Abstract Supplement$ecvp_page</font>\n";
  }
  elsif ($start_page==0 && $authorline2){
    $yearstr="$year, " if $year>0;
    print "$authorline2, $yearstr\"$title\" <i>$journalname</i> advance online publication, doi:10.1068/$paperid</font>\n"
  }
  elsif (($ptype==0||$ptype==1||$ptype==2||$ptype==5||$ptype==8||$ptype==10||$ptype==16||$ptype==12||$ptype==13||$ptype==14||$ptype==15) && $authorline2 && $journal ne 'H'){
    print "$authorline2, $year, \"$title\" <i>$journalname</i> <b>$volume</b>($issue) $start_page&nbsp;&#8211;&nbsp;$end_page</font>\n";
    print br,"  <font size='-2'><a href='ris.cgi?id=$paperid'>Download citation data in RIS format</a></font>";
  }
  elsif (($ptype==0||$ptype==1||$ptype==2||$ptype==5||$ptype==8||$ptype==10||$ptype==16||$ptype==12||$ptype==13||$ptype==15) && $authorline2 && $journal eq 'H'){
    print "$authorline2, $xyear, \"$title\" <i>$journalname</i> <b>$xvolume</b>($issue) $start_page&nbsp;&#8211;&nbsp;$end_page</font>\n";
  }
  elsif ($ptype==9 && $authorline2){  # supplement
    print "$authorline2, $year, \"$title\" <i>$journalname</i> <b>$volume</b> Supplement, $page_prefix$start_page&nbsp;&#8211;&nbsp;$page_prefix$end_page</font>\n";
  }
  #####
  
  
  if($ptype==5){print p,b("<font size='-1'>Editorial</font><br><font size='+2'>$title</font>")}
  elsif($ptype==1){print p,b("<font size='-1'>Guest Editorial</font><br><font size='+2'>$title</font>")}
  elsif($ptype==6){print p,b("<font size='-1'>Obituary</font><br><font size='+2'>$title</font>")}
  elsif($ptype==2){print p,b("<font size='-1'>Commentary</font><br><font size='+2'>$title</font>")}
  elsif($ptype==10){print p,b("<font size='-1'>Last but not least</font><br><font size='+2'>$title</font>")}
  elsif($ptype==16){print p,b("<font size='-1'>Short and sweet</font><br><font size='+2'>$title</font>")}
  elsif($ptype==12){print p,b("<font size='-1'>Review essay</font><br><font size='+2'>$title</font>")}
  elsif($ptype==13){print p,b("<font size='-1'>Letter to the editor</font><br><font size='+2'>$title</font>")}
  elsif($ptype==15){print p,b("<font size='-1'>Featured graphic</font><br><font size='+2'>$title</font>")}
  elsif($ptype==11){print p, "The following books have been received for reviewing:"}
  elsif($ptype==14){
    $sth2=$dbh->prepare("select ptype14 from issues where journal='$journal' and volume=$volume and issue=$issue");
    $sth2->execute();
    ($type14text)=$sth2->fetchrow();
    print p,b("<font size='-1'>$type14text</font><br><font size='+2'>$title</font>")
  }
  else {print p, "<font size='+2'><b>$title</b></font>"} 
  print  p, b($authorline) if $authorline; 
  if ($paperid=~/d2606td/) { print "<br>(English translation by Amaleena Damle, Matei Candea)\n";}
  if ($paperid=~/dst3/) { print " (translated by Mary Varney Rorty)\n";}
  if ($paperid=~/dst2/) { print " (translated by Samuel A Butler)\n";}
  if ($paperid=~/dst1/) { print " (translated by Eduardo Mendieta)\n";}
  print "<p>$received\n" if ($ptype==0&&!$ecvp);
  if ($abstract =~ /\w/ && $abstract !=~ /^None\./){
    print "<p><b>Abstract. </b>" unless ($ptype==3||$ptype==8||$ptype==11||$ecvp);
    
    # filter out any stray 3B2 codes, replace graphics with entities, etc
    # TODO: speed up by making these changes in DB
    $abstract =~ s/<\?.+?>//g;
    $abstract =~ s/<img.+?(\w+?).jpg".*?>/<i>&$1;<\/i>/gi;
    $abstract =~ s/<=/&#x2264;/g;
    $abstract =~ s/ >=/ &#2265;/g;
    $abstract =~ s/<p><a href=.*<\/a>//;
    
    print "$abstract\n";
  }
  
  # create a link to any misc stuff
  if($misc =~ /\w+/){
    print p, "This article has supplementary online material: <a href='misc.cgi?id=$paperid$pw_string'>$misc</a>";
  }
  


  if (-e "ranking_$lower{$journal}.html") {
    open(IN,"ranking_$lower{$journal}.html"); # looks for file with title, for example, ranking_c.html
    $found=0;
    while (<IN>) {
      if ($found==0 && $_ =~ /(abstract.cgi\?id=)(.*?)(">)/ig) {
	$popular = $2;
	$found=1;
      }
    }
    close(IN);
    if ($popular eq $id) {
 	     print "<p><div id='popular'><p><b>Most downloaded paper:</b> This paper has received more downloads than any other EP$journal paper over the last 12 months. <br>Click <a href=\"ranking_$lower{$journal}.html\">here</a> to see the full list of the most downloaded papers.</div>"
    } else {
     # print "<p>This paper is $id. The most popular $journal paper is $popular\n"
    }
  }
  $thisip=$ENV{REMOTE_ADDR};
  if($FUNKYTEST){print "<p><b>Changing IP to test mode:</b><p>";$thisip = $FALSEIP;} #Test on false ip
  #$thisip='192.9.200.236' if $thisip eq '127.0.0.1'; #kludge to enable access on proton5
  #$thisip='152.78.209.160';   # !!!!! comment this out !!!!!!
  #$thisip= '150.237.199.247'; # !!!! comment this out !!!!

  if ($start_page){
    $matchcode= "$journal.*".substr($year, 2, 2)} # a normal paginated article
  else {
    $matchcode= "$journal.*".substr($thisyear, 2, 2) # a forthcoming article - check for current subscription
  }
  
  #if per, matchcode='xxxxxxxx' (ie don't match anything) if year <1999,  else 2000 for other journals  
  if(($journal eq 'P' && $year < 1999) || ($journal =~ /(A|B|C|D)/ && $year<2000)){    #was 2000 for ABCD   
    $matchcode='xxxxxxxxxx';
  }
  
  $matchcode2=$journal.substr($year, 2, 2);
  $current_sub= "$journal.*".substr($thisyear, 2, 2);
  #If a subscription is added as 2013 as it is near the end of the year 2012
  #and the user did not subscribe in 2012, the back archive will not work
  #$future_sub (this year +1) was added to catch this case
  $future_sub=  "$journal.*".substr($thisyear+1, 2, 2);#RFC: Catch the case where a subscritpion is added at end of year
  $cy2=substr($thisyear, 2, 2);
  $ten_year_archive='';
  for($yearx=$thisyear; $yearx>=$thisyear-10; $yearx--){
    $ten_year_archive.= "'".$journal.substr($yearx,2,2)."',";
  }
  $ten_year_archive =~ s/,$//;
  
  if ($journal eq 'P' && $year>=$thisyear-10){
    $matchcode='^O?'.$matchcode;                        #  replaced '^' by '^O?' to cope with OPER11 
    $current_sub='^O?'.$current_sub ;  # to avoid prod~/.*P.*07/ when prod='XP07'
  }

#Sync vars
$prodyear_xxxx=$year;
$prodyear=substr($prodyear_xxxx, 2, 3);
if($FUNKYTEST) {print "Prodyear:".$prodyear_xxxx." ";}
     if ($prodyear_xxxx<$thisyear-10){
       if($journal eq 'P'){
         $access=$dbh->prepare("select count(*) from access, subscribers where access.client=subscribers.client and '$thisip'::CIDR <<= ip  and (prod in ('XPE','XP') or (prod ~ '$journal.*$prodyear' and $prodyear_xxxx > 1998) or prod ~ '^X.*$cy2' or subscribers.client=9902 or (subscribers.client=10049 and $prodyear_xxxx>=1997))");
       }
       else {
         $access=$dbh->prepare("select count(*) from access, subscribers where access.client=subscribers.client and '$thisip'::CIDR <<= ip  and (prod in ('XPE','XE') or (prod ~ '$journal.*$prodyear' and $prodyear_xxxx > 1998) or prod ~ '^X.*$cy2' or (prod~'$matchcode' and $prodyear_xxxx=2000) or subscribers.client=9902 or (subscribers.client=10049 and $prodyear_xxxx>=1997))")  
      }
    } 
    else {
      $access=$dbh->prepare("select count(*) from access, subscribers where access.client=subscribers.client and '$thisip'::CIDR <<= ip  and (prod ~ '$journal.*$prodyear' or prod ~ '$matchcode' or ((prod ~ '$current_sub' or prod ~ '$future_sub') and '$journal$prodyear' in ($ten_year_archive)) or subscribers.client=9902 or subscribers.client=10049)" );  #9902 is Google Scholar's crawler, 10049=SWETS proxy   
 

   } 
       
  
  $paperid=~s/\s+$//;
  
  if ($same_as=~/\w/){
    $same_as=~s/\s*$//;
    $pdf="$same_as.pdf"; # print "<p><font size='-1'>(Part of a composite article.)</font>";
  } else {
    $pdf="$paperid.pdf" 
  }
 if($FUNKYTEST) {print "SQL:<br>".$access->{Statement}."<br>";} 
  $access->execute();
  
  ($ipcount)=$access->fetchrow();

  print p, "<font color='red'><b>FUNCTIONAL IP TEST ON (Remove in code as FUNKYTEST=0): Add IP as 'falseip' in URL. For example abstract.cgi?id=p2885&falseip=143.232.118.148" if ($FUNKYTEST); 
  print p, "<font color='red'><b>DIAGNOSTIC: $second, $minute, $hour, $dayOfMonth, $month, \$thisip=$thisip, \$ipcount=$ipcount, \$matchcode=$matchcode</b></font>" if ($diagnostic eq 'y' || $FUNKYTEST); 

  $uid=get_uid($matchcode,$journal);
  
  #$ipcount=0; # to simulate nonauthorised access 
  #$ipcount=1; # to simulate authorised access 
  #$pw=1; # to simulate password access

  #Allow openaccess
  if($openaccess || $paper_open) {$ipcount=1;}
  $iss_padded = sprintf("%02d", $issue);     # 2-digit volume
  $year2=$year;
  $year2 =~ s/^\d\d//;  # 2-digit year   
   # print "$pdfpath{$journal}$volume/$id.pdf";
  if ($start_page==0){$subdir='forth'} else {$subdir=sprintf("%02d", $volume)}
  if (-e "$pdfpath{$journal}$subdir/$pdf")
  {  # If PDF exists
    $myreal_Filesize= -s "$pdfpath{$journal}$subdir/$pdf";
    $filesize= int(($myreal_Filesize)/1024+0.5);
    if ($journal eq "P")
    {
      $pdfurl="$pdfpath{$journal}$subdir/$pdf";
      #$pdfurl=~s/perception\///;      
    }
    else 
    { 
      $pdfurl="$pdfpath{$journal}$subdir/$pdf";
      if ($pw==1){$pdfurl=~s/^ep/pw_ep/} # point to password-controlled area 
      #$pdfurl=~s/ep//;
    }
   
    

    if ($uid)
    {
      print p, "<a href=\"getpdf.cgi?id=$paperid\"><img src='Images/pdficon_small.gif' alt='PDF' border=0></a>&nbsp;<a href=\"getpdf.cgi?id=$paperid\" onClick=\"return popitup2('getpdf.cgi?id=$paperid')\"><b>Full-text PDF</b></a>&nbsp;<font size='-2'>size: $filesize Kb</font>";
      print " (PDF contains more than one article, please turn to page $start_page.)" if $same_as=~/\w/; 
    }
    elsif ($ipcount>0 )
    {
      #openaccess, make a symlink and change path
      if($openaccess || $paper_open)
      {
        #Make DIR
        unless ( -e "openaccess/") {makedir("openaccess/") || die ("Can't make dir");};
        unless (-e "openaccess/$pdf")
        {
          symlink("../$pdfurl", "openaccess/$pdf");
        }        
        $pdfurl="openaccess/$pdf";
      }
      #Remove openaccess
      if(!($openaccess || $paper_open)){ unlink("openaccess/$pdf"); }      
      print p, "<a href=\"$pdfurl\"><img src='Images/pdficon_small.gif' alt='PDF' border=0></a>&nbsp;<a href=\"$pdfurl\" onClick=\"return popitup2('$pdfurl')\"><b>Full-text PDF</b></a>&nbsp;<font size='-2'>size: $filesize Kb</font>";
      print " (PDF contains more than one article, please turn to page $start_page.)" if $same_as=~/\w/; 
      print "<p><font size='-2'>Some scanned PDFs in this volume may not be up to our usual standards, but should nevertheless be readable. We will place higher quality versions online as soon as possible.</font>\n" if ($journal =~/(B|D)/ && $year<2000) && !($journal eq 'B' && $volume==26 && $issue==2) && !($journal eq 'D' && $volume==17 && $issue==5);
    } # TODO: if $uid link to getpdf.cgi?id=$id&vol=$subdir
    else 
    {
      print p, "<p><font size='-1'><b>Restricted material:</b></font><p><img src='Images/pdficon_bw.gif' alt='PDF' border=0>&nbsp;<font color='gray'><u>Full-text PDF</u>&nbsp;<font size='-2'>size: $filesize Kb</font></font>";
    }
      
    
    #print " (Password controlled)" if $pw==1;
    #print "<p><a href=\"ppv.cgi?id=$id\">Purchase article</a>";
  }


  elsif (-e "$edpdfpath{$journal}/$pdf"){
    $free_ed=1;
    $filesize= int((-s "$edpdfpath{$journal}/$pdf")/1024+0.5);
    if ($journal eq "P"){    
      $pdfurl="$edpdfpath{$journal}/$pdf";
      #$pdfurl=~s/mperception/m/;
      }
    else { 
      $pdfurl="$edpdfpath{$journal}/$pdf";
      #$pdfurl=~s/ep//;
      } 
    print "<p><img src='Images/pdficon_small.gif'>&nbsp;<a href=\"$pdfurl\" target=\"_blank\"><b>Full-text PDF</b></a>&nbsp;<font size='-2'>size: $filesize Kb</font>\n";
      print " (PDF contains more than one article, please turn to page $start_page.)" if $same_as=~/\w/; 
    }
    
  elsif ($journal eq 'P' && ($ptype==1 || $ptype==5) && -e "perception/perc$iss_padded$year2/editorial.pdf"  ){
    $free_ed=1;
    $pdfurl="perception/perc$iss_padded$year2/editorial.pdf";
    print "<p><img src='Images/pdficon_small.gif'> <a href=\"$pdfurl\" target=\"_blank\">Full-text PDF</a>\n";
  }
  elsif ($journal eq 'P' && -e "perception/perc$iss_padded$year2/$pdf"){
    $filesize= int((-s "perception/perc$iss_padded$year2/$pdf")/1024+0.5);
    $pdfurl="perception/perc$iss_padded$year2/$pdf";
    print "<p><img src='Images/pdficon_small.gif'><a href=\"$pdfurl\" target=\"_blank\"><b>Full-text PDF</b></a>&nbsp;<font size='-2'>size: $filesize Kb</font>\n"; 
  }
  else{
    $nofull=1;
    print "<p><font size='-1'>We regret that the PDF of this article is not yet available. We are working to rectify this as quickly as possible.</font>\n" unless ($ptype==11||$ecvp||$journal eq 'H');
    if ($journal eq 'H'){
      if($abstract){
        print "<p><font size='-1'>PDF currently unavailable for this article.</font>"
      } else {
        print "<p><font size='-1'>Abstract and PDF currently unavailable for this article.</font>"
      }
    }
    #print "<p>(There is no full text for ECVP abstracts.)\n" if $ecvp;
  }
   if($ecvp){
     $filesize= int((-s "ecvp/ecvp$year2.pdf")/1024+0.5);
     print p, "<font size='-1'>These web-based abstracts are provided for ease of seaching and access, but certain aspects (such as as mathematics) may not appear in their optimum form. For the final published version of this abstract, please see</font><br><img src='Images/pdficon_small.gif'><a href=\"ecvp/ecvp$year2.pdf\">ECVP $year Abstract Supplement (complete)</a> <font size='-2'>size: $filesize Kb</font>\n" unless $filesize==0;
     print p,"<font size='-1'>[<b>Publisher's note:</b> The abstracts in this year's ECVP supplement have been published with virtually no copy editing by Pion, thus the standards of grammar and style may not match those of regular <i>Perception</i> articles.]</font>" if $year>=2008;
   }

 #if (-e "$refpath{$journal}$volume/xrefs/$id"."refs.html"){
 #   if ($journal eq "P"){
 #    $refurl="http://www.perceptionweb.com$refpath{$journal}$volume/xrefs/$id"."refs.html";
 #    $refurl=~ s/perception//;
 #   }
 #   else {
 #    $refurl="$refpath{$journal}$volume/xrefs/$id"."refs.html";
 #    $refurl=~ s/ep//;
 #   }
 #  print p;
 
 #   }
     
 
    #$paperid=$same_as if $same_as;  # watch this!!
  
    $countrefs=$dbh->prepare("select count(*) from refs where paperid='$paperid'")||die "problem with database";
    $countrefs->execute()||die "problem with database";
    ($refcount)=$countrefs->fetchrow();
    print p;
    
    if($refcount>0 && $year>=1999){
      if($ipcount>0||$uid||$free_ed){
        print "<a href=\"ref.cgi?id=$paperid\"><img src='Images/html2.gif' width='18' alt='HTML' border='0'></a>&nbsp;<a href=\"ref.cgi?id=$paperid\">References</a>&nbsp;&nbsp;" ;
      }
      else{
	  #print p, "<b>PDFs and References are currently unavailable owing to a technical problem. We are working on the problem and hope to have this resolved as soon as possible. Thank you for your patience.</b>";
        print "<img src='Images/html2.gif' width='18' alt='HTML' border='0'>&nbsp;<font color='gray'><u>References</u></font>&nbsp;&nbsp;"
      }
      $countdoi=$dbh->prepare("select count(*) from refs where paperid='$paperid' and doi is not null")||die "problem with database";
      $countdoi->execute()||die "problem with database";
     ($doicount)=$countdoi->fetchrow();
      if ($ipcount>0||$uid||$free_ed){print "<font size='-2'>"} else {print "<font size='-2' color='gray'>"}
      print "$refcount references, $doicount with DOI links ";
      print "(<img src='Images/crossref_small.gif' width= 55 alt='Crossref' border=0>)</font>";
      print "<br>We regret that password-controlled access to linked references is not yet available." if $pw==1;
    }
    
    if($year<$thisyear-10){
      $extra_text='This content is part of our deep back archive.';
    } else {
      #$extra_text="Access is free to institutional subscribers with a current subscription.";
    }
  
    print p, "<font size=-1>Your computer (IP address: $thisip) has not been recognised as being on a network authorised to view the full text or references of this article. $extra_text If you are a member of a university library that has a subscription to the journal, please contact your serials librarian (<a href='subscriptions.html'>subscriptions information</a>).</font>" unless $nofull||$pw==1||$ipcount>0||$free_ed||$uid; # Alternatively, you may <a href=\"ppv.cgi?id=$id\">purchase this article</a>.</font>
#print p, "We regret that access to full text is temporarily unavailable owing to an unexpected problem which are are aiming to fix as quickly as possible. We apologise for any inconvenience." unless $nofull||$pw==1||$ipcount>0||$free_ed||$uid; # Alternatively, you may <a href=\"ppv.cgi?id=$id\">purchase this article</a>.</font>
  #}
  
      # now check for SFX server info
    $sfx_query=$dbh->prepare("select name, openurl_base, open_gif, linker_text from client_details, access where access.client=client_details.client and '$thisip'::CIDR <<= ip");
    $sfx_query->execute();
    ($name, $base, $gif, $link_text)=$sfx_query->fetchrow();
    $sfxtext = "OpenURL link for $name" if $name;
    $link_text=$sfxtext unless $link_text;
    if ($base =~ /\w+/ && $ptype != 11){
      print p, "<a href='$base?genre=article&amp;issn=$issn{$journal}&amp;date=$year&amp;volume=$volume&amp;issue=$issue&amp;spage=$start_page&amp;aulast=$openurl_author_surname&amp;auinit=$openurl_author_initials&amp;sid=pion&amp;doi=10.1068/$paperid' onClick=\"return popitup('$base?genre=article&amp;issn=$issn{$journal}&amp;date=$year&amp;volume=$volume&amp;issue=$issue&amp;spage=$start_page&amp;aulast=$openurl_author_surname&amp;auinit=$openurl_author_initials&amp;sid=pion&amp;doi=10.1068/$paperid')\"><img src='$gif' alt='$link_text' title='$link_text' border='0'></a>&nbsp;<a href='$base?genre=article&amp;issn=$issn{$journal}&amp;date=$year&amp;volume=$volume&amp;issue=$issue&amp;spage=$start_page&amp;aulast=$openurl_author_surname&amp;auinit=$openurl_author_initials&amp;sid=pion&amp;doi=10.1068/$paperid' onClick=\"return popitup('$base?genre=article&amp;issn=$issn{$journal}&amp;date=$year&amp;volume=$volume&amp;issue=$issue&amp;spage=$start_page&amp;aulast=$openurl_author_surname&amp;auinit=$openurl_author_initials&amp;sid=pion&amp;doi=10.1068/$paperid')\"></a>"}
       
      #print p, "<a href='$base?id=$doi' onClick=\"return popitup('$base?id=$doi')\"><img src='$gif' alt='SFX' border='0'></a>&nbsp;<a href='$base?id=$doi' onClick=\"return popitup('$base?id=$doi')\">$sfxtext</a>"}; # 
    
    print p,"<font size='-1'>Advance Online Publications are papers that have been accepted and fully prepared for publication but are yet to appear in an issue of the printed journal. They therefore have not yet been allocated volume and page numbers, and the year is also subject to change. However, the content of the articles should remain unchanged in their final printed form. Each article has a Digital Object Identifier (DOI) which will provide a persistent link to the paper even in it's final form, and may be used for citation purposes (for example, doi:10.1068/p1234 has the URL http://dx.doi.org/10.1068/p1234).</font>" if ($start_page == 0 && !$ecvp && !$ptype==11);  
    
    print "<p><font size='-2'>(You are logged in as $username. <a href='logout.cgi'>Logout.</a>)</font>" if $uid;

    print br,br;    
print <<END;
<!-- AddThis Button BEGIN -->
<script type="text/javascript">addthis_pub  = 'pion';</script>
<a href="http://www.addthis.com/bookmark.php" onmouseover="return addthis_open(this, '', '[URL]', '[TITLE]')" onmouseout="addthis_close()" onclick="return addthis_sendto()"><img src="http://s9.addthis.com/button1-bm.gif" width="125" height="16" border="0" alt="" /></a><script type="text/javascript" src="http://s7.addthis.com/js/152/addthis_widget.js"></script>
<!-- AddThis Button END -->
END

    print <<END; 
      <div class="space"></div>
      <div id="footer">
	<div class="left">
	  <i>$jname{$journal}</i>
        </div>
	<div class="right">
	  Copyright &copy;&nbsp;$thisyear a <a href="http://www.pion.co.uk">Pion</a> publication
        </div>
      </div>
    </div>
END
  #print "<p>&copy; $thisyear a Pion publication\n";
  $authquery->finish();
}


#$sth->finish();


#$dbh->disconnect();

print end_html;


sub secure{
  #return only a single block of alphanumerics to prevent SQL hacking, etc 
  my $input=$_[0];
  $input=~s/\W//g; # delete any non-alpha chars
  return $input;
}
  
