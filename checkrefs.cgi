#!/bin/perl
#  checkrefs.cgi


use URI;
use LWP::UserAgent;
use LWP::Simple;
use File::Glob ':glob';
use CGI qw(:standard -no_xhtml);
use DBI;

$dbh = DBI->connect("dbi:Pg:dbname=journals;host=localhost;port=5432", "jon", "")||die "couldn't connect";

$error=0;
$refnum=0;

$id=param('id');

print header(-type=>'text/html', -charset=>'utf-8', -expires=>'600');
print start_html(-style=>"pion.css", -title=>"Ref checker", -dtd=>'-//W3C//DTD HTML 4.0 Transitional//EN');

unless ($id){
  
  print "<form>Enter paper id: <input name='id' size='10' maxlength='10'><input type='submit'></form>";
  
  print end_html;
  exit;
}
  print p, "Checking references for file $id";
  if($id=~/(^p)/){
    $filename="/i/per/$id.3d"}
  elsif($id=~/(^a)/){
    $filename="/i/epa/$id.3d"}
  elsif($id=~/(^b)/){
    $filename="/i/epb/$id.3d"}
  elsif($id=~/(^c)/){
    $filename="/i/epc/$id.3d"}   
  elsif($id=~/(^d)/){
    $filename="/i/epd/$id.3d"}  
  
  $jletter=uc($1);
    
  unless (-e $filename){
    print p,"File $filename doesn't exist, please try again", end_html;
    exit;
  }
  
  open(FILE3D, "$filename");
  
  
  while(<FILE3D>){
    if (/^\$<(refs|refs_cut)>/){
      &joinup;
      #print "$filename: $_\n";
      if(/fdt/){last;}
   #   s/<refs>(<\?tf=".*">?)//; # delete <refs> and any font garbage
      s/<(refs|refs_cut)>//;
      #print p, "xx $_";
      s/<\?tf="t00.">( |)<\?tf="t00(.)">/$1<?tf="t00$2">/; # remove redundancies
      if(s/(.*?)(\d\d\d\d)(.*?)<\?tf="t002">(.*)<\?tf="t005">(.*?)(\d+)(.*?)<\?tf="t001">(.*?)(\d+)/$1$2$3<i>$4<\/i><b>$5$6$7<\/b>$8$9/i){
        #a candidate for CrossRef!  (Added space in "(.*?) (\d+)" 7/11/05
        $refnum++;
        #if(/<?tf=(.*?)>/g){print "\n\nWarning: Extra <?tf=$1> in $_\n";
        #$error++;}
        
        # $_ contains the HTML reference.
         
#print p, $_; 

       if (/(.+?),.*?(\d\d\d\d).*"(.+?)".*<i>(.+?)\s*<\/i>\s*?<b>\s*(\d+)\s*<\/b>\D*\((\d+)\)\D*.*;\D*(\d+)/){ 
          $name=$1; $cyear=$2; $title=$3; $journal=$4; $issue=$6; $volume=$5; $fpage=$7; $lpage=$8;
          #print "name=$name, cyear=$cyear, journal='$journal', issue=$issue, volume=$volume, page=$page\n\n";
          #$name=$dbh->quote(get_surname($name));
          #print " surname=$name ";
          #$journal=$dbh->quote($journal);
          #remove '$journal' below 
        }
        elsif (/(.+?),.*?(\d\d\d\d).*"(.+?)".*<i>(.+?)\s*<\/i>\s*?<b>\s*(\d+)\s*<\/b>\D*(\d+)\D*.*;\D*(\d+)/){
#        elsif (/(.+?),.*?(\d\d\d\d).*"(.+?)".*<i>(.+?)\s*<\/i>\s*?<b>\s*(\d+)\s*<\/b>\D*(\d+)\D*(\d+)/){
          $name=$1; $cyear=$2; $title=$3; $journal=$4; $volume=$5; $fpage=$6; $lpage=$7;
          #print "name=$name, cyear=$cyear, journal='$journal',  volume=$volume, page=$page\n\n";
          #$name=$dbh->quote(get_surname($name));
          #$journal=$dbh->quote($journal);
          #print " surname=$name ";

        }
        else {

      #unrecognised

        }



         #print p,"$name, cyear=$cyear, journal=$journal, 3=$3, 5=$5, volume=$volume, page=$page";

         if($journal eq 'Perception'){
           $jrnl='P'}
         elsif ($journal =~ /Environment and Planning A/){
           $jrnl='A'}
        elsif ($journal =~ /Environment and Planning B/){
           $jrnl='B'}
        elsif ($journal =~ /Environment and Planning C/){
           $jrnl='C'}
        elsif ($journal =~ /Environment and Planning D/){
           $jrnl='D'}
        else {next};

        print p,"<font color=\"#FF0000\"> $name, $cyear, \"$title\" $journal <b>$volume</b> $fpage &#8211; $lpage <\/font>";

        # now try to find this in the DB

        $sth=$dbh->prepare("select papers.paperid, first_name, last_name, title, year, start_page, end_page, volume from papers, authors where papers.paperid=authors.paperid and journal='$jrnl' and (volume=$volume and start_page=$fpage or volume=$volume and end_page=$lpage) and position in (select min(position) from authors where paperid=papers.paperid)");

        $sth->execute();

        ($paperid, $fname, $lname, $title_db, $year_db, $start_page_db, $end_page_db, $volume_db)=$sth->fetchrow();

        $fname=~s/^(\w).*/$1/;

        print "<br><font color=\"#0000FF\"> <!--$paperid--> $lname $fname, $year_db,  \"$title_db\" $journal <b>$volume_db</b> $start_page_db &#8211; $end_page_db <\/font>";
     }
   }
}
close(FILE3D);
print "<p>File checked";
print end_html;


sub joinup {
  my $temp=$_;
  until (/<>/){
    $_=<FILE3D>;
    if ($_ eq "\r\n"){last}
    $temp .= $_;  #join to previous line
  }
 # $temp=&to_unicode($temp);
  $temp =~ s/\\\n\r/ /g; # remove eol markers
  $temp =~ s/\n\r//g;
  $temp =~ s/\n//g;
  $temp =~ s/\r//g;
  $temp =~ s/\$//g; # remove initial $
  $temp =~ s/\\//g;
  $temp =~ s/&underscore;/_/g;
  $temp =~ s/&#38>;/&amp;/g;
 # $temp =~ s/<\?tbklnk=.*>(.*?)<\?tbklnk>/\[a href="$1"\]$1\[\/a\]/g; #uncomment to activate authors' links
  $temp =~ s/<\?tbklnk=.*>(.*?)<\?tbklnk>/$1/g;
  # remove any 3b2 tag other than a font change to avoid eg 2<twt>5=25
  $temp =~ s/<\?tf=(.*?)>/\[\?tf=$1\]/g;
  $temp =~ s/<.+?>//g;
  $temp =~ s/\[\?tf=(.*?)\]/<\?tf=$1>/g;
  $temp =~ s/\[(|\/)(a.*?)\]/<$1$2>/g;
  # cope with simple font changes in a paper title (up to 3 times)
  $temp =~ s/\`\`(.*?)<\?tf="t002">(.*?)<\?tf="t001">(.*?)\'\'/\`\`$1<i>$2<\/i>$3\'\'/;
  $temp =~ s/\`\`(.*?)<\?tf="t002">(.*?)<\?tf="t001">(.*?)\'\'/\`\`$1<i>$2<\/i>$3\'\'/;
  $temp =~ s/\`\`(.*?)<\?tf="t002">(.*?)<\?tf="t001">(.*?)\'\'/\`\`$1<i>$2<\/i>$3\'\'/;
  $temp =~ s/<\?tf="t041">//gi;
  # remove consecutive font changes
#  $temp =~ s/<\?tf=.*?>(<\?tf=.*?>)/$1/g;
  # replace "Nature (London)" with just "Nature"
  $temp =~ s/Nature \(London\)/Nature/g;
  $temp =~ s/(\`\`|\'\')/"/g;
  # convert to HTML entities....
#  $temp =~ s/&#38>;/&amp;/g;
  $temp =~ s/(&#128;|&#129;|&#146;|&#6;)/ /g;
  $temp =~ s/&#5;/<br>/g;
  $temp =~ s/&#132;//g;
  $temp =~ s/(---)/-/g;
  $temp =~ s/<>//g;
  #accents

#  $temp =~s/(.)\xE8/&$1acute\;/g;
#  $temp =~s/(.)\xE9/&$1grave\;/g;
#  $temp =~s/(.)\xEA/&$1circ\;/g;
#  $temp =~s/(.)\xEB/&$1uml\;/g;
#  $temp =~s/(.)\xEC/&$1tilde\;/g;
#  $temp =~s/(.)\xED//g;
#  $temp =~s/(.)\xEF/&$1ring;/g;
#  $temp =~s/(.)\xEG//g;
#  $temp =~s/\xF5C/&Ccedil;/g;
#  $temp =~s/\xF5c/&ccedil;/g;
#  $temp =~s/\xCC/&auml;/g;
#  $temp =~s/\xCE/&ouml;/g;
#  $temp =~s/\xEB/S/g;
#  $temp =~s/\xEC/s/g;
#  $temp =~s/\xCF/&uuml;/g;

$temp=&to_unicode($temp);

  $_ = $temp;
 # print "$_\n\n"; #debug

}


sub get_auths {
 # print "in get_auths\n";
 &joinup2;
 #print "BEFORE". "$_\n";
 for($authornum=0; /<given_name>/; $authornum++){
   s/<given_name>(.*?)<\/given_name>//;
   $given_name[$authornum] = &to_unicode($1);
   s/<surname>(.*?)<\/surname>//;
   $surname[$authornum] = &to_unicode($1);
  # print " AFTER "; print "$authornum\n";
  # print ">>>$_\n"
 }
}

sub joinup2 {
  my $temp=$_;
  until (/^\r\n/){
#    print "-- $_\n";
    $_=<FILE3D>;
    $temp .= $_;  #join to previous line
  }
  $temp =~ s/\\\n\r/ /g; # remove eol markers
  $temp =~ s/\n\r//g;
  $temp =~ s/\n//g;
  $temp =~ s/\r//g;
  $temp =~ s/\\//g;
  $temp =~ s/\$//g; # remove initial $
  $_ = $temp;
}

sub to_unicode {
  my $temp=$_;
  $_=$_[0];
  s/(&#129;|&#146;|&#128)/ /g; # space codes
  s/&#132;//g;
  s/&#6;/ /g;
  #s/(e\xE8|\xC5)/&#x00E9;/g; #e acute
  #s/(e\xE9|\xC9)/&#x00E8;/g; #e grave
  #s/(u\xEB|\xCF)/&#x00FC;/g; #u umlaut
  #s/(U\xEB|\xDB)/&#x00DC;/g; #U umlaut
  #<eric>
#  s/A\xE9/&#x00C0;/g;  #A grave
#  s/A\xE8/&#x00C1;/g;  #A acute
#  s/A\xEA/&#x00C2;/g;  #A circumflex
#  s/A\xEC/&#x00C3;/g;  #A tilde
#  s/A\xEB/&#x00C4;/g;  #A umlaut
#  s/A\xEF/&#x00C5;/g;  #A ring
#  s/A\xD3/&#x00C6;/g;  #AE
#  ### s/(C\x??|\xB4)/&#x00C7;/g;  #C cedilla
#  s/E\xE9/&#x00C8;/g;  #E grave
#  s/E\xE8/&#x00C9;/g;  #E acute
#  s/E\xEA/&#x00CA;/g;  #E circumflex
#  s/E\xEB/&#x00CB;/g;  #E umlaut
#  s/I\xE9/&#x00CC;/g;  #I grave
#  s/I\xE8/&#x00CD;/g;  #I acute
#  s/I\xEA/&#x00CE;/g;  #I circumflex
#  s/I\xEB/&#x00CF;/g;  #I umlaut
#  ### s/(C\x??|\xE3)/&#x00D0;/g;  #D Eth
#  #s/\xB6/&#x00D1;/g;  #N tilde
#  s/N\xB5/&#x00D1;/g;  #N Tilde
#  s/O\xE9/&#x00D2;/g;  #O grave
#  s/O\xE8/&#x00D3;/g;  #O acute
#  s/O\xEA/&#x00D4;/g;  #O circumflex
#  s/O\xEC/&#x00D5;/g;  #O tilde
#  s/O\xEB/&#x00D6;/g;  #O umlaut
#  ### s/(C\x??|\xBE)/&#x00D7;/g;  #x multiply
#  s/\xD2/&#x00D8;/g;  #O slash
#  s/U\xE9/&#x00D9;/g;  #U grave
#  s/U\xE8/&#x00DA;/g;  #U acute
#  s/U\xEA/&#x00DB;/g;  #U circumflex
#  s/U\xEB/&#x00DC;/g;  #U umlaut
#  s/Y\xE8/&#x00DD;/g;  #Y acute
#  s/\xF0/&#x00DE;/g;  # Thorn
#  s/\xDE/&#x00DF;/g;  # german ss
#  s/a\xE9/&#x00E0;/g;  #a grave
#  s/a\xE8/&#x00E1;/g;  #a acute
#  s/a\xEA/&#x00E2;/g;  #a circumflex
#  s/a\xEC/&#x00E3;/g;  #a tilde
#  s/a\xEB/&#x00E4;/g;  #a umlaut
#  s/a\xEF/&#x00E5;/g;  #a ring
#  s/a\xD3/&#x00E6;/g;  #ae
#  ###  s/(c\x??|xB5)/&#x00E7;/g;  #c cedilla
#  s/e\xE9/&#x00E8;/g;  #e grave
#  s/e\xE8/&#x00E9;/g;  #e acute
#  s/e\xEA/&#x00EA;/g;  #e circumflex
#  s/e\xEB/&#x00EB;/g;  #e umlaut
#  s/i\xE9/&#x00EC;/g;  #i grave
#  s/i\xE8/&#x00ED;/g;  #i acute
#  s/i\xEA/&#x00EE;/g;  #i circumflex
#  s/i\xEB/&#x00EF;/g;  #i umlaut
#  ### s/(C\x??|xE4)/&#x00F0;/g;  #d eth
#  #s/\xB7/&#x00F1;/g;  #n tilde
#  s/n\xB5/&#x00F1;/g;  #n tilde
#  s/o\xE9/&#x00F2;/g;  #o grave
#  s/o\xE8/&#x00F3;/g;  #o acute
#  s/o\xEA/&#x00F4;/g;  #o circumflex
#  s/o\xEC/&#x00F5;/g;  #o tilde
#  s/o\xEB/&#x00F6;/g;  #o umlaut
#  ### s/(C\x??|\xBC)/&#x00F7;/g;  #x divide
#  s/\xD6/&#x00F8;/g;  #o slash
#  s/u\xE9/&#x00F9;/g;  #u grave
#  s/u\xE8/&#x00FA;/g;  #u acute
#  s/u\xEA/&#x00FB;/g;  #u circumflex
#  s/u\xEB/&#x00FC;/g;  #u umlaut
#  s/\xF5c/&#231;/g; #c cedilla
#  s/s\xE8/&#x015B;/g;  #s acute


# CHECK FOR ACCENTS AND CONVERT #

# Neil's additions #
s/<\?tf="pi3">&#142;2&#144;<\?tf="t002">/<sup>&#153;<\/sup>/g; # raised TM
#s/<\?tf="pi3">&#142;2&#144;<\?tf="t002">/<sup><font size=-2><small>TM<\/small><\/font><\/sup>/g; # raised TM
s/&#142;\xF5R&#144;/<sup><font size=-2>&#169;<\/font><\/sup>/g; # raised copyright symbol
s/&#142;(.{1,100}?)&#144;/<sup><font size=2>$1<\/font><\/sup>/g; # raise and lower
s/&#143;(.{1,100}?)&#144;/<sub><font size=2>$1<\/font><\/sub>/g; # lower and raise
s/A\xEE/&#197;/g; # A ring
s/a\xEE/&#229;/g; # a ring 
s/\xF5\[/&#338;/g; # ligature oe
s/\xF5\{/&#339;/g; # ligature OE
s/\xF5e/&#230;/g; # lower case æ
s/\xF5E/&#198;/g; # upper case æ
s/\xF5Q/&#216;/g; # upper case nordic o
s/\xF5q/&#248;/g; # lower case nordic o
s/&emdash;/&#8212;/g; # replace em dashes
s/--/&#8211;/g; # replace en dashes
s/\xF5C/&#199;/g;# C cedilla
s/\xF5c/&#231;/g;# c cedilla
s/\xF5i/&#305;/g;# replace dotless i
s/c\xF5;/&#231;/g;# replace c cedilla?
s/C\xF5;/&#199;/g;# replace C cedilla?
s/s\xF5;/&#351;/g;# s cedilla doesn't work?
s/\xF5k/&#240;/g; # lower case Icelandic "eth"
s/O\xB5/&#336;/g; # double acute
s/o\xB5/&#337;/g; # double acute
s/U\xB5/&#368;/g; # double acute
s/u\xB5/&#369;/g; # double acute
# ----------------- #

#replace letters with dots above
s/A\xE7/&#193;/g;
s/I\xE7/&#304;/g;
#replace acute accents
s/A\xE8/&#193;/g;
s/a\xE8/&#225;/g;
s/E\xE8/&#201;/g;
s/e\xE8/&#233;/g;
s/I\xE8/&#314;/g;
s/i\xE8/&#237;/g;
s/U\xE8/&#218;/g;
s/u\xE8/&#250;/g;
s/O\xE8/&#211;/g;
s/o\xE8/&#243;/g;
s/Y\xE8/&#221;/g;
s/y\xE8/&#253;/g;
s/C\xE8/&#262;/g;
s/c\xE8/&#263;/g;
s/Z\xE8/&#377;/g;
s/z\xE8/&#378;/g;
s/L\xE8/&#313;/g;
s/l\xE8/&#314;/g;
s/N\xE8/&#323;/g;
s/n\xE8/&#324;/g;
s/R\xE8/&#341;/g;
s/r\xE8/&#342;/g;
#replace grave accents
s/E\xE9/&#200;/g;
s/e\xE9/&#232;/g;
s/e\$\xE9/&#232;/g;
s/A\xE9/&#192;/g;
s/a\xE9/&#224;/g;
#replace circumflexes
s/I\xEA/&#206;/g;
s/i\xEA/&#238;/g;
s/A\xEA/&#194;/g;
s/a\xEA/&#226;/g;
s/E\xEA/&#202;/g;
s/e\xEA/&#234;/g;
s/C\xEA/&#264;/g;
s/c\xEA/&#265;/g;
s/O\xEA/&#212;/g;
s/o\xEA/&#244;/g;
s/U\xEA/&#219;/g;
s/u\xEA/&#251;/g;
#replace umlaut accents
s/E\xEB/&#203;/g;
s/e\xEB/&#235;/g;
s/I\xEB/&#207;/g;
s/i\xEB/&#239;/g;
s/A\xEB/&#196;/g;
s/a\xEB/&#228;/g;
s/O\xEB/&#214;/g;
s/o\xEB/&#246;/g;
s/U\xEB/&#220;/g;
s/u\xEB/&#252;/g;
s/y\xEB/&#255;/g;
#replace tildes
#s/(\xEC)C/&#199;/g;
#s/(\xEC)c/&#231;/g;
s/O(\xEC)/&#203;/g;
s/o(\xEC)/&#245;/g;
s/A\xEC/&#195;/g;
s/a\xEC/&#227;/g;
s/N\xEC/&#209;/g;
s/n\xEC/&#241;/g;
#replace carons
s/C\xED/&#268;/g;
s/c\xED/&#269;/g;
s/D\xED/&#270;/g;
s/d\xED/&#271;/g;
s/E\xED/&#282;/g;
s/e\xED/&#283;/g;
s/S\xED/&#352;/g;
s/s\xED/&#353;/g;
s/I\xED/&#463;/g;
s/i\xED/&#464;/g;
s/N\xED/&#327;/g;
s/n\xED/&#328;/g;
#replace ring symbol
s/A\xEE/&#197;/g;
s/a\xEE/&#229;/g;
#replace breve symbol
s/A\xEF/&#258;/g;
s/a\xEF/&#259;/g;
s/E\xEF/&#276;/g;
s/e\xEF/&#277;/g;
s/G\xEF/&#286;/g;
s/g\xEF/&#287;/g;
s/I\xEF/&#300;/g;
s/i\xEF/&#301;/g;
s/O\xEF/&#334;/g;
s/o\xEF/&#335;/g;
#replace opening quotes symbol
s/\xAA/&#8220;/g;
#replace closing quotes symbol
s/\xBA/&#8221;/g;
#replace e acute symbol
s/\xC5/&#233;/g;
#replace Angstrom symbol (fixed cap A)
s/\xD4/&#197;/g;
#replace  nordic O (with line through it) symbol
s/\xD6/&#216;/g;
#replace ae dipthong symbol
s/\xD7/&#230;/g;
#replace i with two dots above symbol
s/\xDD/&#239;/g;
#replace i with two dots above symbol
s/\xDE/&#223;/g;
#replace cedillas and dotless i (two ways to make c cedilla!)
s/\xF5C/&#199;/g;
s/\xF5c/&#231;/g;
s/c\xF5;/&#231;/g;
s/C\xF5;/&#199;/g;
s/s\xF5;/&#351;/g;
s/\xF5i/&#305;/g;
# end of accent replacement


#  s/(A\xE9|\xA1)/&#x00C0;/g;  #A grave
#  s/(A\xE8|\xE0)/&#x00C1;/g;  #A acute
#  s/(A\xEA|\xA2)/&#x00C2;/g;  #A circumflex
#  s/(A\xEC|\xE1)/&#x00C3;/g;  #A tilde
#  s/(A\xEB|\xD8)/&#x00C4;/g;  #A umlaut
#  s/(A\xEF|\xD0)/&#x00C5;/g;  #A ring
#  s/(A\xD3|\xD3)/&#x00C6;/g;  #AE
#  ### s/(C\x??|\xB4)/&#x00C7;/g;  #C cedilla
#  s/(E\xE9|\xA3)/&#x00C8;/g;  #E grave
#  s/(E\xE8|\xDC)/&#x00C9;/g;  #E acute
#  s/(E\xEA|\xA4)/&#x00CA;/g;  #E circumflex
#  s/(E\xEB|\xA5)/&#x00CB;/g;  #E umlaut
#  s/(I\xE9|\xE6)/&#x00CC;/g;  #I grave
#  s/(I\xE8|\xE5)/&#x00CD;/g;  #I acute
#  s/(I\xEA|\xA6)/&#x00CE;/g;  #I circumflex
#  s/(I\xEB|\xA7)/&#x00CF;/g;  #I umlaut
#  ### s/(C\x??|\xE3)/&#x00D0;/g;  #D Eth
#  s/(\xB6)/&#x00D1;/g;  #N tilde
#  s/(O\xE9|\xE8)/&#x00D2;/g;  #O grave
#  s/(O\xE8|\xE7)/&#x00D3;/g;  #O acute
#  s/(O\xEA|\xDF)/&#x00D4;/g;  #O circumflex
#  s/(O\xEC|\xE9)/&#x00D5;/g;  #O tilde
#  s/(O\xEB|\xDA)/&#x00D6;/g;  #O umlaut
#  ### s/(C\x??|\xBE)/&#x00D7;/g;  #x multiply
#  s/(\xD2)/&#x00D8;/g;  #O slash
#  s/(U\xE9|\xAD)/&#x00D9;/g;  #U grave
#  s/(U\xE8|\xED)/&#x00DA;/g;  #U acute
#  s/(U\xEA|\xAE)/&#x00DB;/g;  #U circumflex
#  s/(U\xEB|\xDB)/&#x00DC;/g;  #U umlaut
#  s/(Y\xE8)/&#x00DD;/g;  #Y acute
#  s/(\xF0)/&#x00DE;/g;  # Thorn
#  s/(\xDE)/&#x00DF;/g;  # german ss
#  s/(a\xE9|\xC8)/&#x00E0;/g;  #a grave
#  s/(a\xE8|\xC4)/&#x00E1;/g;  #a acute
#  s/(a\xEA|\xC0)/&#x00E2;/g;  #a circumflex
#  s/(a\xEC|\xE2)/&#x00E3;/g;  #a tilde
#  s/(a\xEB|\xCC)/&#x00E4;/g;  #a umlaut
#  s/(a\xEF|\xD4)/&#x00E5;/g;  #a ring
#  s/(a\xD3|\xD7)/&#x00E6;/g;  #ae
#  ###  s/(c\x??|xB5)/&#x00E7;/g;  #c cedilla
#  s/(e\xE9|\xC9)/&#x00E8;/g;  #e grave
#  s/(e\xE8|\xC5)/&#x00E9;/g;  #e acute
#  s/(e\xEA|\xC1)/&#x00EA;/g;  #e circumflex
#  s/(e\xEB|\xCD)/&#x00EB;/g;  #e umlaut
#  s/(i\xE9|\xD9)/&#x00EC;/g;  #i grave
#  s/(i\xE8|\xD5)/&#x00ED;/g;  #i acute
#  s/(i\xEA|\xD1)/&#x00EE;/g;  #i circumflex
#  s/(i\xEB|\xDD)/&#x00EF;/g;  #i umlaut
#  ### s/(C\x??|xE4)/&#x00F0;/g;  #d eth
#  s/(\xB7)/&#x00F1;/g;  #n tilde
#  s/(o\xE9|\xCA)/&#x00F2;/g;  #o grave
#  s/(o\xE8|\xC6)/&#x00F3;/g;  #o acute
#  s/(o\xEA|\xC2)/&#x00F4;/g;  #o circumflex
#  s/(o\xEC|\xEA)/&#x00F5;/g;  #o tilde
#  s/(o\xEB|\xCE)/&#x00F6;/g;  #o umlaut
#  ### s/(C\x??|\xBC)/&#x00F7;/g;  #x divide
##  s/(\xD6)/&#x00F8;/g;  #o slash
#  s/(u\xE9|\xCB)/&#x00F9;/g;  #u grave
#  s/(u\xE8|\xC7)/&#x00FA;/g;  #u acute
#  s/(u\xEA|\xC3)/&#x00FB;/g;  #u circumflex
#  s/(u\xEB|\xCF)/&#x00FC;/g;  #u umlaut

  s/(y\xE8)/&#x00FD;/g;  #y acute
  s/(\xF1)/&#x00FE;/g;  # thorn
  s/&#38;/&#x0026;/g; #ampersand
  #</eric>
  # s/<.*?>//g; # remove 3B2 spacing codes
  my $retval=$_;
  $_=$temp;
  return $retval;
}
