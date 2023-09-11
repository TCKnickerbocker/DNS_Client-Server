<h1>Thomas Knickerbocker,02/14/2023<br>
python3,DNSServer.py,,DNSServer.py</h1><br>

<h3><u>Compilation</u></h3>
<ol>
    <li>In a shell/terminal, enter "python3 DNSServer.py"</li>
    <li>In a separate terminal, enter "python3 DNSClient.py"</li>
</ol><br>

<h3><u>Running</u></h3>
<ol>
    <li>In the client terminal, type in the alias of the servers you wish to get the ip addresses of (i.e. www.mysite.com</li>
    <li>When done on the client side, enter "q" or "Q" into the terminal</li>
    <li>When done on the server side, enter "exit" into the terminal</li>
    <li>DNS_mapping.txt will now contain information regarding your session, and dns-server-log.csv will now contain a record of every query executed</li>
</ol><br>

<h3><u>Description</u></h3>
<div>
    <h5>This program:</h5>
    <ul>
        <li>Allows users to get the ip addresses of sites they enter</li>
        <li>Keeps a neat, comma-separated log of requests from the user</li>
        <li>Keeps a  re-uable mapping of Hostnames:IPs to optimize future performance time</li>
        <li>Will always return the ip address of a website which results in the lowest ping</li>
    </ul>
</div>