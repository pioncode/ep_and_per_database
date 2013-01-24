#!/usr/bin/perl 
# CGI script to display references. 
# Usage: .../ref.cgi?id=p1234
# 

use DBI;
use CGI qw(:standard -no_xhtml);
require('getuid.pl');

@weekDays = qw(Sun Mon Tue Wed Thu Fri Sat Sun);
($second, $minute, $hour, $dayOfMonth, $month, $yearOffset, $dayOfWeek, $dayOfYear, $daylightSavings) = localtime();
$thisyear = 1900 + $yearOffset;
$month++;

%refpath=(
 "P" => "perception/abstracts/p",
 "A" => "ep/epa/abstracts/a",
 "B" => "ep/epb/abstracts/b",
 "C" => "ep/epc/abstracts/c",
 "D" => "ep/epd/abstracts/d"  
);

%edpdfpath = (
 "P" => "perception/editorials",
 "A" => "epa/editorials",
 "B" => "epb/editorials",
 "C" => "epc/editorials",
 "D" => "epd/editorials"
);

%jname= (
 "P" => "Perception",
 "A" => "Environment and Planning A",
 "B" => "Environment and Planning B: Planning and Design",
 "C" => "Environment and Planning C: Government and Policy",
 "D" => "Environment and Planning D: Society and Space"
);

%jid=(
 "P" => "per",
 "A" => "epa",
 "B" => "epb",
 "C" => "epc",
 "D" => "epd"
);

%issn=(
 "P" => "0301-0066",
 "A" => "0308-518X",
 "B" => "0265-8135",
 "C" => "0263-774X",
 "D" => "0263-7758"
);  


$id=secure(param('id'));
$pw=param('pw');

$pw_string='&pw=1' if $pw==1;

$journal=uc(substr($id,0,1));  # fix to get journal from id for testing free access

print header;


$dbh = DBI->connect("dbi:Pg:dbname=journals;host=localhost;port=5432", "jon", "")||die "couldn't connect";
$sth=$dbh->prepare("select year, journal, title, volume, issue, page_prefix, start_page, end_page from papers where paperid='$id';") || die;
$sth->execute()||die "Can't execute query\n";
@result=$sth->fetchrow();
($year, $journal, $title, $volume, $issue, $page_prefix, $start_page, $end_page)=@result;
if(-e "$edpdfpath{$journal}/$id.pdf"){
  $ipcount=1;  #enable free access for editorials
}
else {
  $thisip=$ENV{REMOTE_ADDR};
  #$thisip='192.9.200.236' if $thisip='127.0.0.1'; #kludge to enable access on proton5

#--------- copied from abstract.cgi ------------------- 
  if ($start_page){
    $matchcode= "$journal.*".substr($year, 2, 2)} # a normal paginated article
  else {
    $matchcode= "$journal.*".substr($thisyear, 2, 2) # a forthcoming article - check for current subscription
  }
  
  $matchcode2=$journal.substr($year, 2, 2);
  $current_sub= "$journal.*".substr($thisyear, 2, 2);
  $ten_year_archive='';
  for($yearx=$thisyear; $yearx>=$thisyear-10; $yearx--){
    $ten_year_archive.= "'".$journal.substr($yearx,2,2)."',";
  }
  $ten_year_archive =~ s/,$//;
  
  if ($journal eq 'P' && $year>=$thisyear-10){
    $matchcode='^'.$matchcode;
    $current_sub='^'.$current_sub ;  # to avoid prod~/.*P.*07/ when prod='XP07'
  }

  #if (($month==1||$month==2) && ($year==$thisyear||$start_page==0)){
  #  $grace_prod = "$journal.*".substr($thisyear-1,2,2); # match prev year's sub in January/February
  #}
  #else {
  #  $grace_prod = 'xxxxxxxxxxxxxxxx';  # ensure match fails
  #}  
  
   if ($year<$thisyear-10){
      if($journal eq 'P'){
        $access=$dbh->prepare("select count(*) from subscribers, access where subscribers.client=access.client and '$thisip'::CIDR <<= ip and (prod in ('XPE','XP') or prod ~ '^X.*$current_sub' or subscribers.client in (9902,10049))");
      }
      else {
        $access=$dbh->prepare("select count(*) from subscribers, access where subscribers.client=access.client and '$thisip'::CIDR <<= ip and (prod in ('XPE','XE') or prod ~ '^X.*$current_sub' or subscribers.client in (9902,10049))")  
      }
   } 
  else {
       $access=$dbh->prepare("select count(*) from subscribers, access where subscribers.client=access.client and '$thisip'::CIDR <<= ip and (prod ~ '$matchcode' or (prod ~ '$current_sub'  and '$matchcode2' in ($ten_year_archive)) or subscribers.client in (9902,10049))  and deny is not true") ;
  }  
#------------------------------------  
  
  
#  $matchcode= "$journal.*".substr($year, 2, 2);
#  $matchcode2=$journal.substr($year, 2, 2);
#  $current_sub= "$journal.*".substr($thisyear, 2, 2);
#  $ten_year_archive='';
#  for($yearx=$thisyear; $yearx>$thisyear-10; $yearx--){
#    $ten_year_archive.= "'".$journal.substr($yearx,2,2)."',";
#  }
#  $ten_year_archive =~ s/,$//;
#  $access=$dbh->prepare("select count(*) from subscribers, access where subscribers.client=access.client and '$thisip'::CIDR <<= ip and (prod ~ '$matchcode' or (agent='KESL' and prod ~ '$current_sub' and '$matchcode2' in ($ten_year_archive)))  and deny is not true");
  $access->execute();
  ($ipcount)=$access->fetchrow();
  
#  $ipcount=1 if $thisip=~/192\.9\.200\.\d+/;  #temp fix for Pion
  #$ipcount=0;  # uncomment for testing access control
}


if ($ipcount==0 && not get_uid($matchcode)){  #&& not get_uid()
  print start_html,  p, "Your computer has not been recognised as being part of a network authorised to view the references of this article. Access is free to institutional subscribers who have purchased the corresponding volume of this journal in printed form. Please contact your serials librarian.";
  print p, "<a href='http://www.envplan.com/'>Environment and Planning home page</a>" if $journal=~/(A|B|C|D)/; 
  print end_html; exit}
elsif (@result==0){print "No matching abstract", end_html; exit}
else{
  #($year, $journal, $title, $volume, $issue, $page_prefix, $start_page, $end_page)=@result;
  $journalname=$jname{"$journal"};

$jscript= "
var newwindow;\n
function popitup(url) {\n
	newwindow=window.open(url,'SFXmenu','location=no, status=yes, menubar=no, scrollbars=yes, resizable=yes, width=460');\n
	if (window.focus) {newwindow.focus()}\n
	return false;\n
}\n
\n
function popitup2(url) {\n
	newwindow=window.open(url,'ftext','location=no, status=yes, menubar=no, scrollbars=yes, resizable=yes');\n
	if (window.focus) {newwindow.focus()}\n
	return false;\n
}\n
";  
    
  print start_html(-style=>"pion.css", -title=>"Pion references", -id=>$jid{$journal},
  -dtd=>'-//W3C//DTD HTML 4.0 Transitional//EN', -meta=>{'ROBOTS'=>'NOARCHIVE'}, -script=>$jscript);

  $gif=lc($journal).'_ban.gif';
  $banner="<img src=\"Images/$gif\" alt=\"$jname{$journal}\" border=0 class=\"logo\">" if  $journal=~/(A|B|C|D)/;
  
  #$banner='<img src="Images/ep_left_ban.gif" alt="environment and planning" border=0 class="logo">' if $journal=~/(A|B|C|D)/;
  $banner='<img src="Images/p_ban2.gif" alt="Perception" border=0 class="logo">' if $journal eq 'P';
  
  $j_name=$jname{$journal};
  
  if ($journal eq 'P'){
    $buttons="<li><a href=\"P.html\" title=\"View Perception homepage\">Perception&nbsp;homepage</a></li>";
  } else {
    $buttons="<li><a href=\"$journal.html\" title=\"View $j_name homepage\">EP$journal&nbsp;homepage</a></li>
            <li><a href=\"index.html\" title=\"View EP homepage\">EP&nbsp;homepage</a></li>";
  }          
  
  if ($start_page){
    $dateline="<b>$year</b> volume <a href='contents.cgi?journal=$journal&amp;volume=$volume'><b>$volume</b></a>(<a href='contents.cgi?journal=$journal&amp;volume=$volume&amp;issue=$issue'>$issue</a>) pages $page_prefix$start_page&nbsp;&#8211;&nbsp;$page_prefix$end_page";
  } else {
    $dateline="Advance online publication"
  }
  print <<END;
      <div id="header">
      <a href="$journal.html">$banner</a>
      <a href="http://www.pion.co.uk"><img src="Images/right_ban.gif" alt="Pion Ltd" class="pionlogo" /></a>
    </div>
    <div id="total">
      <div id="top-buttons">
	<div class="topnavigation">
	  <ul>
	    <li><a href="search.cgi?journal=$journal" title="Search all papers">Search</a></li>
	    <li><a href="contents.cgi?journal=$journal&amp;issue=current" title="View latest issue">Current&nbsp;issue</a></li>
	    <li><a href="contents.cgi?journal=$journal&amp;volume=forthcoming" title="View advance online publications">Forthcoming</a></li>
	    <li><a href="allvols.cgi?journal=$journal" title="View all published volumes">All&nbsp;volumes</a></li>
            $buttons
	  <li><a href="http://www.pion.co.uk" title="Go to Pion ltd homepage">Pion&nbsp;homepage</a></li>
	  </ul>
	</div>
      </div>
      <div id="title">
	<div class="left"><font size=4>$dateline</font></div>
	<div class="center"></div>
	<div class="right"></div>
      </div>
   
END

# print p, "<b>We regret that this page does not currently display correctly in Internet Explorer 7.0.  We intend to correct this as quickly as possible, but in the meantime please use a previous version or <a href='http://getfirefox.com'>Firefox</a>.</b><br><br>" if $ENV{'HTTP_USER_AGENT'} =~ /MSIE 7\.0/;  
  
  #print "<i>$journalname</i> $year volume <a href='contents.cgi?journal=$journal&volume=$volume$pw_string'><b>$volume</b></a> $start_page&#8211;$end_page\n";
  #print h1('References');
  print "<br><font size='+1'><b>$title</b></font><br>";
  
  $authquery=$dbh->prepare("select first_name, last_name, suffix from authors where paperid='$id' order by position")||die;
  $authquery->execute()||die;
  
  $authlist="";
  while (@author=$authquery->fetchrow()){
    ($first_name,$last_name,$suffix)=@author;
    $suffix='&nbsp;'.$suffix if $suffix;
    $authlist .= "$first_name&nbsp;$last_name$suffix, ";
    if ($first_name =~ s/\b(van|de|del|van der|von|von der|van den)\b//i){
      $vans_etc="$1&nbsp;"}
    else
      {$vans_etc=""}    
    $openurl_author_surname="$vans_etc$last_name" unless $openurl_author_surname;
    $initials='';  
    @fnames=split(/ /, $first_name);
    for $fn (@fnames){
      unless($fn=~/-/){
        $fn =~ /(\w|&.*?;).*?\b/; 
        $initials .= "$1 ";
      } else {
        $fn =~ /(\w|&.*?;).*?-(\w|&.*?;)/;
        $initials .= "$1-$2 ";
      }
    }       
    $openurl_author_initials=$initials unless $openurl_author_initials;
    $openurl_author_initials =~ s/ //g;         
  }
  $authlist =~ s/, $//;
  print "<font size=-1>$authlist</font>";
}

if ($journal eq 'P'){$hoststring='http://www.perceptionweb.com/'}
elsif ($journal =~ /(A|B|C|D)/){$hoststring='http://www.envplan.com/'}
print p, "<a href=".$hoststring."abstract.cgi?id=$id>Abstract</a>";

print p, b("<font size='+2'>References</font>");
#print p,p,"<a href='http://www.crossref.org/05researchers/index.html'><img src='Images/crossrefenableds.gif' align='bottom' border='0' class='right' alt='CrossRef enabled'></a>";
#open(REFS, "/htdocs/$refpath{$journal}$volume/xrefs/$id"."refs.html")||die("can't open refs");
#while(<REFS>){
# if (/<p class=ref>/){ 
#   s/<a href="http:\/\/www.envplan.com\/ep.\/abstracts\/.+?\/(.+).html">/<a href='abstract.cgi?id=$1'>/;
#   print}
#}

#print p,"refs from database:";

$sfx_query=$dbh->prepare("select name, openurl_base, open_gif, linker_text from client_details, access where access.client=client_details.client and '$thisip'::CIDR <<= ip");
$sfx_query->execute();
($name, $base, $gif, $link_text)=$sfx_query->fetchrow();

$refq=$dbh->prepare("select unstructured, doi, ref, journal_title, volume, first_page, cyear from refs where paperid='$id' order by ref");
$refq->execute();
while (@row=$refq->fetchrow()){
  ($reftext, $doi, $ref, $journal_title, $j_volume, $j_first_page, $j_year)=@row;
  #next if $reftext eq '<p class=ref>';
  $reftext =~ s/&nbsp;&nbsp;&nbsp;&nbsp;<a href="http:\/\/dx.doi.org.*?<font size="-1">\[CrossRef\]<\/font>/<a href=''>/;
  $reftext =~ s/<a href="http:\/\/(www.envplan.com\/ep.\/abstracts|www.perceptionweb.com\/perabs)\/.+?\/(.+).html">/<a href='abstract.cgi?id=$2'>/; 
  $reftext =~ s/E&P/E&amp;P/;

  #$reftext =~ s/&nbsp;-&nbsp;/&#8211;/g;
  if ($reftext=~ s/^\&#TAB;//){
    print "<br>$reftext";
  } else {
    print '<p class=ref>'.$reftext;
  }
  print ", <a href='http://dx.doi.org/$doi'>doi:$doi</a>" if $doi;
  if ($base =~ /\w+/ && $journal_title && $j_volume &&$ptype != 11 ){
  
    unless ($journal_title =~ /\</){ 
    $journal_title=~s/\s/\%20/g; 
    $journal_title=~s/&amp;/and/g;  
    $linkstring="$base?genre=article&amp;title=$journal_title&amp;date=$j_year&amp;volume=$j_volume&amp;spage=$j_first_page&amp;sid=pion";
    $linkstring.="&amp;doi=$doi" if $doi;
    print " <a href='$linkstring' onClick=\"return popitup('$linkstring')\"><img src='$gif' alt='$link_text' border='0'></a>" ;
    }
  }
  print "\n";
}
print p, "$ref references";

$countdoi=$dbh->prepare("select count(*) from refs where paperid='$id' and doi is not null")||die "problem with database";
$countdoi->execute()||die "problem with database";
($doicount)=$countdoi->fetchrow();

print p, "$doicount <a href='http://www.crossref.org'><img src='Images/crossref_small.gif' alt='CrossRef member' align=bottom border=0></a> DOIs retrieved";

      # now check for SFX server info
    #$sfx_query=$dbh->prepare("select name, openurl_base, open_gif from client_details, access where access.client=client_details.client and '$thisip'::CIDR <<= ip");
    #$sfx_query->execute();
    #($name, $base, $gif)=$sfx_query->fetchrow();
    #$sfxtext = "OpenURL link for $name" if $name;
    
    if ($base =~ /\w+/ && $ptype != 11){
      print p, "<a href='$base?genre=article&amp;issn=$issn{$journal}&amp;date=$year&amp;volume=$volume&amp;issue=$issue&amp;spage=$start_page&amp;aulast=$openurl_author_surname&amp;auinit=$openurl_author_initials&amp;sid=pion&amp;doi=10.1068/$paperid' onClick=\"return popitup('$base?genre=article&amp;issn=$issn{$journal}&amp;date=$year&amp;volume=$volume&amp;issue=$issue&amp;spage=$start_page&amp;aulast=$openurl_author_surname&amp;auinit=$openurl_author_initials&amp;sid=pion&amp;doi=10.1068/$paperid')\"><img src='$gif' alt='$link_text' title='$link_text' border='0'></a>&nbsp;<a href='$base?genre=article&amp;issn=$issn{$journal}&amp;date=$year&amp;volume=$volume&amp;issue=$issue&amp;spage=$start_page&amp;aulast=$openurl_author_surname&amp;auinit=$openurl_author_initials&amp;sid=pion&amp;doi=10.1068/$paperid' onClick=\"return popitup('$base?genre=article&amp;issn=$issn{$journal}&amp;date=$year&amp;volume=$volume&amp;issue=$issue&amp;spage=$start_page&amp;aulast=$openurl_author_surname&amp;auinit=$openurl_author_initials&amp;sid=pion&amp;doi=10.1068/$paperid')\">$sfxtext</a>"};
       

# print p,br, br, br "<a href='abstract.cgi?id=$id$pw_string'>Return to abstract page</a>";

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
print end_html;

 sub secure{
  #return only a single block of alphanumerics to prevent SQL hacking, etc 
  my $input=$_[0];
  $input=~s/\W//g; # delete any non-alpha chars
  return $input;
}
   
