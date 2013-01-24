#!/usr/bin/perl 
# CGI script to generate tables of contents. 
# Usage: .../contents.cgi?journal=P&volume=32
#  volume=forthcoming generates advance online publications
#  volume missing generates the current volume contects
#  volume

#

use DBI;
use CGI qw(:standard -no_xhtml);
#use DateTime;
#use DateTime::Format::Strptime;    # for NEW! on forthcoming

@weekDays = qw(Sun Mon Tue Wed Thu Fri Sat Sun);
($second, $minute, $hour, $dayOfMonth, $month, $yearOffset, $dayOfWeek, $dayOfYear, $daylightSavings) = localtime();
$thisyear = 1900 + $yearOffset;
$month++;

$journal=secure(param('journal'));
$virt=secure(param('virt'));
$volume=secure(param('volume'));
$iss=secure(param('issue'));
$year=secure(param('year'));
$pw=param('pw');
if ($pw==1){
  $pw_string="\&pw=1";
  $pw_string2 = "<input type=hidden name=pw value=$pw>"
}

%jname= (
 "V" => "Perception ECVP Abstract Supplement",
 "P" => "Perception",
 "H" => "High Temperatures-High Pressures",
 "A" => "Environment and Planning A",
 "B" => "Environment and Planning B: Planning and Design",
 "C" => "Environment and Planning C: Government and Policy",
 "D" => "Environment and Planning D: Society and Space"
);

%vnames= (
 "V" => "Perception ECVP Abstract Supplement: ",
 "P" => "Perception: ",
 "H" => "High Temperatures-High Pressures: ",
 "A" => "Environment and Planning A: ",
 "B" => "Environment and Planning B: ",
 "C" => "Government and Policy: ",
 "D" => "Society and Space Special Issue: "
);

%jid=(
 "H" => "hthp",
 "P" => "per",
 "A" => "epa",
 "B" => "epb",
 "C" => "epc",
 "D" => "epd"
);


%startyear=(
 "H" => 1969,
 "P" => 1972,
 "A" => 1969,
 "B" => 1974,
 "C" => 1983,
 "D" => 1983
);

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

$volume=$year-$startyear{$journal}+1 if $year;

$dbh = DBI->connect("dbi:Pg:dbname=journals;host=localhost;port=5432", "jon", "")||die "couldn't connect";
$findlastvol=$dbh->prepare("select max(volume) from issues where journal='$journal'") || die;
$findlastvol->execute()||die "Can't execute query\n";
($maxvol)=$findlastvol->fetchrow();

$findlastiss=$dbh->prepare("select max(issue) from papers where journal='$journal' and volume=$maxvol;")||die;
$findlastiss->execute()||die;
($maxiss)=$findlastiss->fetchrow();

unless($volume){
  $volume=$maxvol;
  $iss=$maxiss if $iss eq 'current'
}

$year = $startyear{$journal}+$volume-1;

unless(($volume eq 'virtual')||($volume eq 'forthcoming')){
  $findlastiss_this=$dbh->prepare("select max(issue) from papers where journal='$journal' and volume=$volume;")||die;
  $findlastiss_this->execute()||die;
  ($maxiss_this)=$findlastiss_this->fetchrow();
}

print header(-charset=>'utf-8',
             -expires=>'600',
            );

$previous_vol=$volume-1;
$next_vol=$volume+1;

$jscript =<<END;
function formHandler(form){
var URL = document.form.site.options[document.form.site.selectedIndex].value;
window.location.href = URL;
}
var newwindow;
function popitup(url) {
	newwindow=window.open(url,'helpmenu','location=no, status=yes, menubar=no, scrollbars=yes, resizable=yes, navigationbar=yes, height=500, width=460');
	if (window.focus) {newwindow.focus()}
	return false;
}
END

#default_dtd('-//W3C//DTD HTML 4.0 Transitional//EN');
if ($journal eq 'H') {
  print start_html(-style=>"pion.css", -title=>$jname{$journal}." contents vol $xvolume", -script=>$jscript, -id=>$jid{$journal}, -head=>Link({-rel=>'alternate', -title=>'Pion RSS feed', -href=>"rss.cgi?journal=$journal", -type=>'application/rss+xml'}),-dtd=>'-//W3C//DTD HTML 4.0 Transitional//EN');
} else {
  print start_html(-style=>"pion.css", -title=>$jname{$journal}." contents vol $volume", -script=>$jscript, -id=>$jid{$journal}, -head=>Link({-rel=>'alternate', -title=>'Pion RSS feed', -href=>"rss.cgi?journal=$journal", -type=>'application/rss+xml'}), -dtd=>'-//W3C//DTD HTML 4.0 Transitional//EN');
  # print start_html($jname{$journal}." contents vol $volume");
}

$thisip=$ENV{REMOTE_ADDR};
if ($thisip=~/171.66.236/ || $thisip eq '128.42.174.11' || $thisip eq '129.79.35.56'){  # insert CLOCKSS IP addresses
  print "<!-- CLOCKSS system has permission to ingest, preserve, and serve this Archival Unit -->\n";
}


if ($maxiss_this>1){
  $issues_string='issue&nbsp;';
  for($i=1; $i<=$maxiss_this; $i++){
   # $issues_string .= "<a href='#$i'>$i</a>&nbsp;|&nbsp;";
   unless($i==$iss){
     $issues_string .= "<a href='contents.cgi?journal=$journal&amp;volume=$volume&amp;issue=$i'>$i</a>&nbsp;|&nbsp;"}
   else{
     $issues_string .= "$i&nbsp;|&nbsp;";
   }
  }
  if($iss){
    $issues_string .= "<a href='contents.cgi?journal=$journal&amp;volume=$volume$pw_string'>all</a>"}
  else {
    $issues_string .= "all"}
}

if ($volume eq 'forthcoming'){
  $contents_heading="Advance online publications";
}
 elsif ($volume eq 'virtual'){
  if($virt eq 'list'){
  $contents_heading="Virtual issues";
  }
  else{
  #Get title from DB
  #
  $sth=$dbh->prepare("select theme_title from virtual_themes where journal='$journal' and virtual_theme_id='$virt'") || die;
  $sth->execute(); 
  $contents_heading=$sth->fetchrow();;
  }
}
  elsif ($journal eq'H') {
  $contents_heading="Volume&nbsp;$xvolume&nbsp;";
} else {
  $contents_heading="Volume&nbsp;$volume&nbsp;";
}

if ($previous_vol>0)
{ $previous= "<A HREF=\"contents.cgi?journal=$journal&amp;volume=$previous_vol$pw_string\"><font size=2 color=teal>Previous volume</font></A>" }


if ($next_vol<=$maxvol){
  $next= "<A HREF=\"contents.cgi?journal=$journal&amp;volume=$next_vol$pw_string\"><font size=2 color=teal>Next volume</font></A>";
}

$gif=lc($journal).'_ban.gif';

$j_name=$jname{$journal};

if ($journal eq 'P'){
  $banner='<img src="Images/p_ban2.gif" alt="Perception" border=0 class="logo">';
  $button1="<a href=\"P.html\" title=\"View Perception homepage\">Perception homepage</a>";
  $button2='<li><a href="ECVP.html" title="ECVP abstracts">ECVP</a></li>';
  $example='';
} elsif ($journal eq 'H'){
  $banner='<img src="Images/h_ban2.gif" alt="High Temperatures - High Pressures" border=0 class="logo">';
  $button1="<a href=\"H.html\" title=\"View High Temperatures - High Pressures homepage\">HTHP homepage</a>";
  $example='';
} elsif ($journal eq 'D'){
  $banner="<img src=\"Images/$gif\" alt=\"$jname{$journal}\" border=0 class=\"logo\">";
  $button1="<a href=\"$journal.html\" title=\"View $j_name homepage\">EP$journal&nbsp;homepage</a>";
  $button2="<a href=\"http://societyandspace.wordpress.com/\" title=\"EPD Blog\">EP$journal&nbsp;blog</a>";
  $button3="<a href=\"index.html\" title=\"View EP homepage\">EP&nbsp;homepage</a>";
  $example='Example: (town or urban) planning';
} else {
  $banner="<img src=\"Images/$gif\" alt=\"$jname{$journal}\" border=0 class=\"logo\">";
  $button1="<a href=\"$journal.html\" title=\"View $j_name homepage\">EP$journal&nbsp;homepage</a>";
  $button2="<a href=\"index.html\" title=\"View EP homepage\">EP&nbsp;homepage</a>";
  $example='Example: (town or urban) planning';
}

  for($i=$maxvol; $i>0; $i--){
    $selected='selected' if $i==$volume;
    $opyear=$startyear{$journal}+$i-1;
    $options_string .= "<option value=\"contents.cgi?journal=$journal&amp;volume=$i$pw_string\" $selected>$i ($opyear)</option>\n";
    $selected='';
    }

if ($journal eq 'H') {
  for($i=$maxvol; $i>26; $i--){
    if ($i==27){
      $j="27/28";
      $opyear="1995/1996";
    } elsif ($i==35) {
      $j="35/36";
      $opyear="2003/2007";
    } else {
      $j=$i;
      $opyear=$startyear{$journal}+$i-1;
    }
    $selected='selected' if $i==$volume;
    if ($i<36 && $i>28 || $i==27) {
      $options_string .= "<option value=\"contents.cgi?journal=$journal&amp;volume=$i$pw_string\" $selected>$j ($opyear)</option>\n";
      $selected='';
    }
  }
}
 elsif ($volume eq 'forthcoming') {
$options_string= "<option value=\"contents.cgi?journal=$journal&amp;volume=forthcoming\">Forthcoming</option> ";
  for($i=$maxvol; $i>0; $i--){
    $selected='selected' if $i==$volume;
    $opyear=$startyear{$journal}+$i-1;
    $options_string .= "<option value=\"contents.cgi?journal=$journal&amp;volume=$i$pw_string\" $selected>$i ($opyear)</option>\n";
    $selected='';
  }
 }
 elsif ($volume eq 'virtual') {
$options_string= "<option value=\"contents.cgi?journal=$journal&amp;volume=virtual\">Virtual issues</option> ";
  for($i=$maxvol; $i>0; $i--){
    $selected='selected' if $i==$volume;
    $opyear=$startyear{$journal}+$i-1;
    $options_string .= "<option value=\"contents.cgi?journal=$journal&amp;volume=$i$pw_string\" $selected>$i ($opyear)</option>\n";
    $selected='';
  }
 }


$year='' if (($volume eq 'forthcoming' )|| ($volume eq 'virtual'));


print <<END;
    
    <div id="header">
      <a href="$journal.html">$banner</a>
      <a href="http://www.pion.co.uk"><img src="Images/right_ban.gif" alt="Pion Ltd" class="pionlogo" /></a>
    </div>
    <div id="total">
      <div id="top-buttons">
	<div class="topnavigation">
	  <ul>
	    <li><a href="search.cgi?journal=$journal$pw_string" title="Search all papers">Search</a></li>
END
unless ($journal eq 'H') {
  print "	    <li><a href=\"contents.cgi?journal=$journal&amp;issue=current$pw_string\" title=\"View latest issue\">Current&nbsp;issue</a></li>";
  print "	    <li><a href=\"contents.cgi?journal=$journal&amp;volume=forthcoming$pw_string\" title=\"View advance online publications\">Forthcoming</a></li>";
  print "           <li><a href=\"allvols.cgi?journal=$journal$pw_string\" title=\"View all published volumes\">All&nbsp;volumes</a></li>";
} else {
  print "           <li><a href=\"allvols_h.html\" title=\"View pre-2008 volumes\">Pre-2008 volumes</a></li>";
}
print <<END;
	    <li>$button1</li>
            <li>$button2</li>
            <li>$button3</li>
	  <li><a href="http://www.pion.co.uk" title="Go to Pion ltd homepage">Pion&nbsp;homepage</a></li>
	  </ul>
	</div>
      </div>
      <div id="title"> 
      <div class="left"><font size=4>$contents_heading&nbsp;$issues_string</font></div>
END
if ($journal=='H') {
  print "	      <div class=\"right\"><font size=4>$xyear</font></div>"; 
} else {
  print "	      <div class=\"right\"><font size=4>$year</font></div>"; 
}

print <<END;
      </div>

   <div id="topspace">
	<div class="search">
	<form method=POST action="search.cgi">
        <font size="-1">
        <table border=0 cellspacing=2>
        <tr>
        <td valign=top align=left>
	 Words or phrase:&nbsp;</td>
        <td align=left>	  <input type=text name = query size=20 maxlength=50>&nbsp;
</td>
<tr>
<td>	 Author (surname):</td>
<td align=left>	  <input type=text name = authorquery size=20 maxlength=50>&nbsp;
</td><tr>
<td><a href="search.cgi?journal=$journal"><font size="-1">More options</font></a></td>
<td align=right><input type=submit value="Search">&nbsp;</td>
</table>

<!--	  <br>$example-->
	  <input type=hidden name=journal value=$journal>
          </font>	    
	</form>
	</div>
	<div class="dropdown"> 

	  <form name="form" action="contents.cgi"><font size="-1">Go to volume</font>
	    <select  onChange="javascript:formHandler(this)" name="site" size=1>
            $options_string
	    </select>&nbsp;&nbsp;</form>
        </div> 
END

unless ($journal eq 'H') { 

  print "  <div class=\"right\"><div class=\"space\"></div><font size=\"-1\"><a href='alerting_services.html' onClick=\"return popitup('alerting_services.html')\">Alerting services:</a></font> 
  <a href=\"http://www.envplan.com/alertregister.cgi?journal=$journal\"><img
                 border=0
                 src=\"Images/email2.jpg\"
                 alt=$jshort{$journal} email alerts
                 align=center
                 height=20
                 title=\"Click to subscribe for email alerts\"
                 /></a>
  <a href=\"rss.cgi?journal=$journal\"><img
                 border=0
                 src='Images/rss_feed.gif'
                 alt='RSS feed'
                 align=center
                 title=\"Click to sign up to RSS feeds\"
                 ></a> </font>

  </div>";
}
  print "      </div>";


#
if ($volume eq 'forthcoming'){
  $sth=$dbh->prepare("select title, abstract, issue, start_page, end_page, page_prefix, papers.paperid, ptype, misc, extract(epoch from (now()-online)) from papers, authors where journal='$journal' and start_page=0 and authors.paperid=papers.paperid and position=0 and virtual_only = FALSE order by online desc, last_name;") || die; 
}
elsif ($volume eq 'virtual'){
  if($virt eq 'list'){
   $sth=$dbh->prepare("
    SELECT virtual_themes.virtual_theme_id, virtual_themes.theme_title, virtual_themes.artist_name, virtual_themes.guesteds,virtual_journals.virtual_theme_order, virtual_themes.openaccess 
    FROM virtual_themes, virtual_journals WHERE virtual_themes.virtual_theme_id=virtual_journals.virtual_theme_id  AND virtual_journals.journal='$journal' 
    ORDER BY virtual_journals.virtual_theme_order
") || die;
  }
  else{
  $sth=$dbh->prepare("
  SELECT papers.title, papers.abstract, papers.issue, papers.start_page, 
  papers.end_page, papers.page_prefix, papers.paperid, papers.ptype, papers.misc, NULL, papers.volume, papers.journal
  FROM papers, virtual_papers
  WHERE papers.paperid = virtual_papers.paperid
  AND virtual_papers.virtual_theme_id='$virt' ORDER BY virtual_papers.paper_order
   ;") || die; 
 
  }
}  
elsif ($iss){
  $sth=$dbh->prepare("select title, abstract, issue, start_page, end_page, page_prefix, paperid, ptype, misc, NULL from papers where journal='$journal' and volume=$volume and issue=$iss and virtual_only = FALSE order by page_prefix desc, start_page;") || die;   
} 
else{
    
   $sth=$dbh->prepare("SELECT title, abstract, issue, start_page, end_page, page_prefix, paperid, ptype, misc, NULL FROM papers where papers.journal='$journal' and papers.volume=$volume and virtual_only = FALSE   ORDER BY page_prefix desc, start_page
   ;") || die;  
}
  
$sth->execute()||die "Cannot execute query\n";
#"

#
#Local
$file=`php ../db/read_static_xml.php $journal forthcoming intro ../db/read_static_text.xml`;
#Server
#$file=`php /cgi-bin/db/read_static_xml.php $journal forthcoming intro /cgi-bin/db/read_static_text.xml`;

print p, $file if $volume eq 'forthcoming';

#print p,"Virtual Issue. The most recently added papers are shown at the top." if $volume eq 'forthcoming';

$this_issue=0;
$rowcount=0;
$refFlag=0;
while (@result=$sth->fetchrow()){
  if($virt eq 'list'){
  ($vir_theme_id,$vir_title,$vir_artist_name,$vir_guesteds)=@result;
  print "<a href=\'contents.cgi?journal=".$journal."&volume=virtual&virt=".$vir_theme_id." \'><p>".$vir_title."</p></a>";
   if ($vir_guesteds){print "<p><small>With guest editors: ".$vir_guesteds."</small></p>";}
  #Done for a virtual issue so return to get next entry
  next;
  }
  ($title, $abstract, $issue, $start_page, $end_page, $page_prefix, $paperid, $ptype, $misc, $time_online, $vir_volume, $vir_journal)=@result;
  $rowcount++;
  if($issue != 0 && $this_issue != $issue){  
    unless ($page_prefix =~ /\w/){
     # if($iss){
        #print "<br><h3><i>$jname{$journal}</i> $year volume $volume issue $issue</h3>"
     # } else {
        if($volume != "virtual") {print "<h3><a name=\"$issue\">Issue $issue</a></h3>\n" ;}
      # }
    }
     
    $this_issue=$issue;
    #print p, $addendum;
    $geditorial=0;  # (re)initialise flag to control whether to print "editorial"
    $editorial=0;
    $commentaries=0;
    $lnl=0;
    $sas=0;
    $letters_editor=0;
    $featured_graphic=0;
    $review_essay=0;
    # check for special issue
    $sth1=$dbh->prepare("select issuetype, heading, subheading, guesteds, theme_start, theme_end, heading2, subheading2, guesteds2, theme_start2, theme_end2, addendum from issues where volume=$volume and issue=$issue and journal='$journal'") || die "xxxx";
    $sth1->execute();
    if (@result1=$sth1->fetchrow()){
      ($issuetype, $heading, $subheading, $guesteds, $theme_start, $theme_end, $heading2, $subheading2, $guesteds2, $theme_start2, $theme_end2, $addendum)=@result1;
      if($addendum){
        # find the last page number of the issue
        $qy=$dbh->prepare("select max(start_page) from papers where journal='$journal' and volume=$volume and issue=$issue");
        $qy->execute();
        ($end_issue)=$qy->fetchrow();
      }
      print "<p><br><b>Supplementary issue</b>\n" if $issuetype==2;
      $special='Special issue: ' if $journal eq 'P';
      if ($heading =~ /\s/ && $theme_start==0){
        print "<p><b>$special$heading</b>\n";
        if ($subheading ne ""){print "<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;$subheading\n"}
        if ($guesteds ne ""){
          if ($guesteds =~ /,/){
            print "<br>Guest editors: $guesteds\n"
          }
          else {
            print "<br>Guest editor: $guesteds\n"
          }
        }
      }
    }   
  }
  
  $paperid =~ s/\s*$//; # delete trailing spaces
  
  #check if theme starts part-way down
  if ($heading && $theme_start==$start_page){
    #$geditorial=0; # reset flag that suppresses 'Guest Editorial' more than once
    print "<p><b>$special$heading</b>\n";
    if ($subheading ne ""){print "<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;$subheading\n"}
    if ($guesteds ne ""){
      if ($guesteds =~ /,/){
        print "<br>Guest editors: $guesteds\n"
      }
      else {
        print "<br>Guest editor: $guesteds\n"
      }
    }
  }
  
  if ($heading2 && $theme_start2==$start_page){
    print "<p><b>$heading2</b>\n";
    if ($subheading2 ne ""){print "<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;$subheading2\n"}
    if ($guesteds2 ne ""){
      if ($guesteds2 =~ /,/){
        print "<br>Guest editors: $guesteds2\n"
      }
      else {
        print "<br>Guest editor: $guesteds2\n"
      }
    }
  }  
  
  
  #check if editorial and whether to use plural
  if ($ptype==1 && $geditorial==0){
    $geditorial=1;  # make sure we only do this once per issue
    # count how many editorials in this issue (-1)
    $sth2=$dbh->prepare("select count(*) from papers where journal='$journal' and volume=$volume and issue=$issue and ptype=1");
    $sth2->execute();
    ($more_than_one_geditorial)=$sth2->fetchrow(); 
    $more_than_one_geditorial--;
    if($volume!="virtual"){         
     if ($more_than_one_geditorial){ 
      print "<p><b>Guest editorials</b><br>\n";}
     else {
      print "<p><b>Guest editorial</b><br>\n";}   
    }
  }
  
  #check if commentary and whether to use plural
  
  if ($ptype==2 && $commentaries==0){
    unless ($volume==26 && $issue==1 && $journal==B) {$commentaries=1;}  # make sure we only do this once per issue
    # count how many editorials in this issue (-1)
    $sth2=$dbh->prepare("select count(*) from papers where journal='$journal' and volume=$volume and issue=$issue and ptype=2");
    $sth2->execute();
    ($more_than_one_comm)=$sth2->fetchrow(); 
    $more_than_one_comm--;
    if ($volume==26 && $issue==1 && $journal==B) {
      print "<p><b>Commentary</b><br>\n";}
    elsif ($more_than_one_comm){ 
      print "<p><b>Commentaries</b><br>\n";}
    else {
      print "<p><b>Commentary</b><br>\n";}   
  }  

  #if($ptype==10&&$lnl==0){$lnl=1}

  if ($ptype==13 && $letters_editor==0){
    $letters_editor=1;
    $sth2=$dbh->prepare("select count(*) from papers where journal='$journal' and volume=$volume and issue=$issue and ptype=13");
    $sth2->execute();
    ($more_than_one_letter_ed)=$sth2->fetchrow(); 
    $more_than_one_letter_ed--;
    if ($more_than_one_letter_ed){ 
      print "<p><b>Letters to the editor</b><br>\n";}
    else {
      print "<p><b>Letter to the editor</b><br>\n"} 
  }
  if ($ptype==5 && $editorial==0){
    $editorial=1;  # make sure we only do this once per issue
    # count how many editorials in this issue (-1)
    $sth2=$dbh->prepare("select count(*) from papers where journal='$journal' and volume=$volume and issue=$issue and ptype=5");
    $sth2->execute();
    ($more_than_one_editorial)=$sth2->fetchrow(); 
    $more_than_one_editorial--;

    if ($more_than_one_editorial){ 
      print "<p><b>Editorials</b><br>\n";}
    else {
      print "<p><b>Editorial</b><br>\n" unless $title eq 'Editorial';}   
  } 
  #if ($ptype==5 && $title ne 'Editorial'){print "<p><b>Editorial</b><br>\n";}
  elsif ($ptype==6){print "<p><b>Obituary</b><br>\n"}
  elsif ($ptype==10&&$lnl==0){print "<p><b>Last but not least</b><br>\n";
                     $lnl=1 unless $lnl}
  elsif ($ptype==16&&$sas==0){print "<p><b>Short and sweet</b><br>\n";
                     $sas=1 unless $sas}

  elsif ($ptype==12 && $review_essay==0){
    $review_essay=1;  # make sure we only do this once per issue
    # count how many editorials in this issue (-1)
    $sth2=$dbh->prepare("select count(*) from papers where journal='$journal' and volume=$volume and issue=$issue and ptype=12");
    $sth2->execute();
    ($more_than_one_review_essay)=$sth2->fetchrow(); 
    $more_than_one_review_essay--;

    if ($more_than_one_review_essay){ 
      print "<p><b>Review essays</b><br>\n";}
    else {
      print "<p><b>Review essay</b><br>\n" unless $title eq 'Review essay';}   

      
  }  elsif ($ptype==15 && $featured_graphic==0){
    $featured_graphic=1;  # make sure we only do this once per issue
    # count how many graphics in this issue (-1)
    $sth2=$dbh->prepare("select count(*) from papers where journal='$journal' and volume=$volume and issue=$issue and ptype=15");
    $sth2->execute();
    ($more_than_one_graphic)=$sth2->fetchrow(); 
    $more_than_one_graphic--;

    if ($more_than_one_graphic){ 
      print "<p><b>Featured graphics</b><br>\n";}
    else {
      print "<p><b>Featured graphic</b><br>\n" unless $title eq 'Featured graphic';}   
  }

  elsif ($ptype==14 && !$ptype14used{$issue}){
    $ptype14used{$issue}=1;
    $sth2=$dbh->prepare("select ptype14 from issues where journal='$journal' and volume=$volume and issue=$issue");
    $sth2->execute();
    ($type14text)=$sth2->fetchrow();
    print "<p><b>$type14text</b><br>\n"
  }

  
  if ($volume eq "forthcoming"){ 
    if ($time_online < 604800){  # 7 days
      $pagestring = "&nbsp;&nbsp;&nbsp;<FONT style=\"BACKGROUND-COLOR: #ffffb6\"><b>&nbsp;Added in last 7 days&nbsp;</b></FONT>"
    } else {
       $pagestring=""
    }
  }

  else{
    if($start_page==$end_page){
      $pagestring="$page_prefix$start_page"
    }
    else
    {
      $pagestring="$page_prefix$start_page&nbsp;&#8211;&nbsp;$page_prefix$end_page";
    }   
   }
  #No page number for virtual issue
  if($volume=="virtual"){$pagestring="";}

  #Fill the abstract link string  
  if($ptype!=9 || $revFlag!=0){$abslink=$pageno."<a href=\"abstract.cgi?id=$paperid$pw_string\"><b>$title</b></a> $pagestring"};
  if($ptype==9 && $revFlag==0){$abslink=$pageno."<br><br><b><span style=\"text-decoration:none\"><font color=\"black\">Reviews</font></span></b><br><a href=\"abstract.cgi?id=$paperid$pw_string\"><b>$title</b></a> $pagestring"; $revFlag=1;}; 
  if ($ptype==1 || $ptype==5 || $ptype==6 || $ptype==2 || $ptype==10 || $ptype==16 || $ptype==12 || $ptype==13 || $ptype==14 || $ptype==15){
   if($volume!="virtual") {print "<div class='ed'>";}
   print $abslink;
   if($volume!="virtual") {print "</div>";}
  }
  else
  {
    if( ($volume eq "virtual") && ($title eq "Reviews") ){print "<p><b>$vnames{$vir_journal} book review for volume $vir_volume, issue $issue </b>$abslink<br>\n";} 
    else 
    {print "<p>$abslink<br>\n";} 
  }   
  if ($ptype==3||$ptype==8 || $ptype==9) {
    $abstract =~ s/^\s*(<br>|<p>)//;
    $abstract =~ s/<br>\s*<br>/<br>/;
    print "<div class='ed'>" if ($ptype==8);
    print "<font size='-1'>$abstract</font>\n"; # make this smaller and indent
    print "</div>" if ($ptype==8);
  }  # reviews


  #print "<p><a href=\"abstract.cgi?id=$paperid\"><b>$title</b></a> $start_page-$end_page<br>\n";
  
  $authquery=$dbh->prepare("select first_name, last_name, suffix from authors where paperid='$paperid' order by position")||die;
  $authquery->execute()||die;
  $authors="";
  while (@author=$authquery->fetchrow()){
    ($first_name,$last_name,$suffix)=@author;
    $suffix='&nbsp;'.$suffix if $suffix;
    $authors .= "$first_name $last_name$suffix, ";
  }
  $authors =~ s/, $//;   # remove final comma space
  if ($ptype==1||$ptype==5||$ptype==6 || $ptype==2 ||$ptype==10 || $ptype==16 || $ptype==12 || $ptype==13 || $ptype==14 || $ptype==15){
   if($volume!="virtual") {$authors='<div class="ed">'.$authors.'</div>'}
   if($volume=="virtual") {$authors='<br/>'.$authors}
  }
  $authors='' if $ptype==8;
  print "$authors\n" if $authors;
  if ($paperid=~/d2606td/) { print "<br>(English translation by Amaleena Damle, Matei Candea)\n";}
  if ($paperid=~/dst3/) { print " (translated by Mary Varney Rorty)\n";}
  if ($paperid=~/dst2/) { print " (translated by Samuel A Butler)\n";}
  if ($paperid=~/dst1/) { print " (translated by Eduardo Mendieta)\n";}
  if ($paperid=~/d13707/) { print " (interviewers)\n";}
   
  if($heading && ($theme_end==$end_page || $theme_end2==$end_page)){print p({-align=>'center'}, "<p>&loz;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&loz;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&loz;<br>"),"\n"}
  
  print p, $addendum if $start_page>=$end_issue;
}

if (($volume eq 'forthcoming') && $rowcount==0){print p, 'No forthcoming papers are currently available. Please check again soon, or subscribe to the RSS feed for automatic delivery of contents.'} 

# Books received
if($volume==$maxvol){
  $brid=lc($journal).'books';
  $brecq=$dbh->prepare("select count(*) from papers where paperid='$brid' and abstract ~ '.(5)'") || die ;
  $brecq->execute() || die ;
  ($booksrec_exists)=$brecq->fetchrow();
  print p,br, br, "<a href='abstract.cgi?id=$brid$pw_string'><b>Books received</b></a>" if $booksrec_exists;
}

if($journal eq 'V'){
  $ecvpq=$dbh->prepare("select count(*) from papers where journal='V' and volume=$volume");
  $ecvpq->execute() ; 
  ($ecvp_count)=$ecvpq->fetchrow();
  print p, br, br, "<a href='ecvp.cgi?year=$year'>European Conference on Visual Perception $year. Abstracts.</a>" if $ecvp_count;
}

print p, "<font size='-1'>Forthcoming papers have not yet been allocated volume and page numbers, and the year is also subject to change. However, the content of the articles should remain unchanged in their final printed form. Each article has a Digital Object Identifier (DOI) which will provide a persistent link to the paper even in its final form, and may be used for citation purposes (for example, doi:10.1068/p1234 has the URL http://dx.doi.org/10.1068/p1234).</font>" if $volume eq 'forthcoming' && $rowcount>0;

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
