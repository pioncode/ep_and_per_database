#!/bin/perl

# ris.cgi

# TODO: deal with advance online, ECVP
use DBI;
use CGI qw(:standard -no_xhtml);
use HTML::Entities;
use Encode;
use Encode::Byte;

%jname= (
 "V" => "Perception ECVP Abstract Supplement",
 "P" => "Perception",
 "H" => "High Temperatures - High Pressures",
 "A" => "Environment and Planning A",
 "B" => "Environment and Planning B: Planning and Design",
 "C" => "Environment and Planning C: Government and Policy",
 "D" => "Environment and Planning D: Society and Space"
);

%issn=(
 "H" => "0018-1544",
 "P" => "0301-0066",
 "A" => "0308-518X",
 "B" => "0265-8135",
 "C" => "0263-774X",
 "D" => "0263-7758"
);  

$id=secure(param('id'));

$dbh = DBI->connect("dbi:Pg:dbname=journals;host=localhost;port=5432", "jon", "")||die "couldn't connect";

$sth=$dbh->prepare("select year, journal, title, volume, issue, abstract, start_page, end_page, page_prefix, paperid, ptype from papers where paperid='$id';") || die;

$sth->execute()||die "Can't execute query\n";
@result=$sth->fetchrow();

if (@result==0){die "No matching abstract $id\n"}

($year, $journal, $title, $volume, $issue, $abstract, $start_page, $end_page, $page_prefix, $paperid, $ptype)=@result;

if($journal eq 'A' && $volume < 6 && $volume>0){$journalname='Environment and Planning'}
  elsif($journal eq 'B' && $volume < 10 && $volume>0){$journalname='Environment and Planning B'}
  else {$journalname=$jname{"$journal"}}

$paperid =~ s/\s//g;
  
#print header(-type=>'application/octet-stream', -attachment=>"$paperid.ris");

if($journal eq 'V'){$ty='CONF'}
elsif($start_page == 0){$ty='INPR'}
else {$ty='JOUR'}

print header(-type=>'application/ris', -attachment=>"$paperid.ris"); 
print "TY  - $ty\r\n"; # TODO: must be ABST for ECVP
  
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
  $suffix_x='';
  $suffix_x=", $suffix" if $suffix;
  $_="$vans_etc$last_name, $initials$suffix_x";
  &convert_symbols;
  $author_out=encode('cp437', decode_entities("$_"));
  
  print "A1  - $author_out\r\n"; 
}
$authorline =~ s/, $//;
$authorline2 =~ s/, $//;

$title =~ s/<.+?>//g;
$title =~ s/ & / &amp; /g;
$_=$title;
&convert_symbols;
$title=encode('cp437', decode_entities($_));


if($journal =~ /(A|B|C|D)/){$url="http://www.envplan.com/abstract.cgi?id=$paperid"}
elsif ($journal =~ /(P|V)/){$url="http://www.perceptionweb.com/abstract.cgi?id=$paperid"}
else {$url='unknown'}

$_=$abstract;
&convert_symbols;
$abstract=encode('cp437', decode_entities($_));

$ID="ID  - 10.1068/$paperid\r\n" unless $journal='V';

print "$ID"."Y1  - $year\r\nT1  - $title\r\nJO  - $journalname\r\nSP  - $start_page\r\n";
print "EP  - $end_page\r\nVL  - $volume\r\nIS  - $issue\r\nUR  - $url\r\nPB  - Pion Ltd\r\n";
print "SN  - $issn{$journal}\r\nN2  - $abstract\r\nER  -\r\n";
  

  

sub secure{
  #return only a single block of alphanumerics to prevent SQL hacking, etc 
  my $input=$_[0];
  $input=~s/\W//g; # delete any non-alpha chars
  return $input;
}  

sub convert_symbols{
  s/(&#8216;|&#8217;)/'/g;
  s/(&#8221;|&#8222;)/"/g;
  s/(&#8211;|&#8212;)/ - /g;
  s/&#176;/\xF8/g;
  s/&#192;/A/g;
  s/&#193;/A/g;
  s/&#194;/A/g;
  s/&#195;/A/g;
  #s /&#196;/A/g;
  #s /&#197;/A/g;
  #s /&#199;/C/g;
  s/&#200;/E/g;
  #s /&#201;/E/g;
  s/&#202;/E/g;
  s/&#203;/E/g;
  s/&#206;/I/g;
  s/&#207;/I/g;
  #s /&#209;/N/g;
  s/&#211;/O/g;
  s/&#212;/O/g;
  #s /&#214;/O/g;
  s/&#216;/O/g;
  s/&#218;/U/g;
  s/&#219;/U/g;
  #s /&#220;/U/g;
  s/&#221;/Y/g;
  #s /&#224;/a/g;
  #s /&#225;/a/g;
  #s /&#226;/a/g;
  s/&#227;/a/g;
  #s /&#228;/a/g;
  #s /&#229;/a/g;
  #s /&#230;/ae|g;
  #s /&#231;/c/g;
  #s /&#232;/e/g;
  #s /&#233;/e/g;
  #s /&#234;/e/g;
  #s /&#235;/e/g;
  #s /&#237;/i/g;
  #s /&#238;/i/g;
  #s /&#239;/i/g;
  #s /&#241;/n/g;
  #s /&#243;/o/g;
  #s /&#244;/o/g;
  s/&#245;/o/g;
  #s /&#246;/o/g;
  s/&#248;/o/g;
  #s /&#250;/u/g;
  #s /&#251;/u/g;
  #s /&#252;/u/g;
  s/&#253;/y/g;
  #s /&#255;/y/g;
  s/&#262;/C/g;
  s/&#263;/c/g;
  s/&#264;/C/g;
  s/&#265;/c/g;
  s/&#268;/C/g;
  s/&#269;/c/g;
  s/&#270;/D/g;
  s/&#271;/d/g;
  s/&#282;/E/g;
  s/&#283;/e/g;
  s/&#286;/G/g;
  s/&#287;/g/g;
  s/&#305;/i/g;
  s/&#305;/i/g;
  s/&#313;/L/g;
  s/&#314;/I/g;
  s/&#314;/l/g;
  s/&#322;/l/g;
  s/&#323;/N/g;
  s/&#324;/n/g;
  s/&#327;/N/g;
  s/&#328;/n/g;
  s/&#341;/r/g;
  s/&#342;/R/g;
  s/&#352;/S/g;
  s/&#353;/s/g;
  s/&#377;/Z/g;
  s/&#378;/z/g;
  s/&#463;/I/g;
  s/&#464;/i/g;
  s/<.+?>//g;
}