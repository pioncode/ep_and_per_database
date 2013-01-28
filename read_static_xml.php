<?php
//Usage: <Journal> <Text Block> <Text section> <xml file>

//Testing:
//Test
 //something to test
//End test

if (!$argv[1]) die ("Error: No Journal in ".$argv[0]."\n");
if (!$argv[2]) die ("Error: No Text block ".$argv[0]."\n");
if (!$argv[3]) die ("Error: No Text section ".$argv[0]."\n");
if (!$argv[4]) die ("Error: No file ".$argv[0]."\n");

$arrData = array(
journal => $argv[1],
textblk => $argv[2],
textsec => $argv[3],
xmlFile => $argv[4],
);

//Test: Check array: 
 //print_r ($arrData);
//End test
//Test: Check filename: 
 //echo $arrData['xmlFile'];
//End test

$xml = simplexml_load_file($arrData["xmlFile"]);
//Test:
 //print_r ($xml); exit;
//End test

//Check to see if the journal is in the list
//Make a counter $i, Record the default text index or replace with the new journal index
$i=0;
$intDefault=0;
$intJournal=-1;
foreach ( $xml->$arrData["textblk"]->$arrData["textsec"] as $arrayXml){
 //Test: Check XML array
  //echo $arrayXml["journal"];
 //End test
 if($arrayXml["journal"]=="default")			{$intDefault=$i;}
 if($arrayXml["journal"]==$arrData["journal"])		{$intJournal=$i;}
 $i++;
}
if($intJournal!=-1){$intDefault=$intJournal;}
//Test vars that come out of loop
 //var_dump ($arrData);
 //echo $intDefault;
 //var_dump ($xml->$arrData["textblk"]->$arrData["textsec"]);
//End Test

echo $xml->$arrData["textblk"]->{$arrData["textsec"]}[$intDefault];
?>

