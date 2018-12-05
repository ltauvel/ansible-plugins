#!powershell
# This file is an Ansible module
#
# Copyright 2016, Ludovic Tauvel <ludovic.tauvel@gmail.com>
# GitHub : https://github.com/ltauvel/
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

# WANT_JSON
# POWERSHELL_COMMON

$params = Parse-Args $args;
$result = New-Object PSObject;
Set-Attr $result "changed" $false;

# Retreive ansible arguments
$name = Get-Attr -obj $params -name name -default '*'
$memory = Get-Attr -obj $params -name memory -default '512MB'
$generation = Get-Attr -obj $params -name generation -default 1
$template = Get-Attr -obj $params -name template -default $null
$diskpath = Get-Attr -obj $params -name diskpath -default $null

$internalswitch = Get-Attr -obj $params -name internalswitch -default 'no'
$internalvlantype = Get-Attr -obj $params -name internalvlantype -default $null
$internalvlanprimary = Get-Attr -obj $params -name internalvlanprimary -default $null
$internalvlansecondary = Get-Attr -obj $params -name internalvlansecondary -default $null
$externalswitches = Get-Attr -obj $params -name externalswitches -default $null

$WaitForIPAddress = Get-Attr -obj $params -name waitforipaddress -default 'no'
$gather_facts = Get-Attr -obj $params -name gather_facts -default 'no'
$type = Get-Attr -obj $params -name gather_type -default 'Connection'

$showlog = Get-Attr -obj $params -name showlog -default "false" | ConvertTo-Bool
$state = Get-Attr -obj $params -name state -default "present" -emptyattributefailmessage "missing required argument: state"

# Check if the Hyper-V feature has been enabled
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
function Test-HyperVEnabled {
	# Get the Hyper-V feature
	$hyperv = Get-WindowsOptionalFeature -FeatureName Microsoft-Hyper-V-All -Online

	return $hyperv.State -eq 'Enabled'
}

# Check if the specified virtual machine exists
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
function Test-VirtualMachineExists {
	if(Get-VM -Name $name) {
		return $true
	}
}

# Create the virtual machine
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
function Create-VirtualMachine {

	$cmd = "New-VM -Name $name"	
	
	if ($memory) {
        $cmd += " -MemoryStartupBytes $memory"
    }
	
	if ($generation) {
        $cmd += " -Generation $generation"
    }
	
	if($templatefile) {
		$diskpath = '{0}\{1}.vhdx' -f (Get-VMHost).VirtualHardDiskPath, $name
		Copy-Item -Path $templatefile -Destination $diskpath
	}
	
	if ($diskpath) {
		#If VHD already exists then attach it, if not create it
		if (Test-Path $diskpath) {
			$cmd += " -VHDPath '$diskpath'"
		}
		else {
			$cmd += " -NewVHDPath '$diskpath'" 
		}  
    }
	
	$results = invoke-expression $cmd
	
	
	if($externalswitches -or $internalSwitch -eq 'yes'){
				
		# Remove the default network adapters created 
		Get-VMNetworkAdapter -VMName $name | Remove-VMNetworkAdapter
		
		# Get the available switches
		$switches = Get-VMSwitch
		
		# Configure internal switch
		if($internalSwitch -eq 'yes') {
			$internalSwitch = $switches | Where-Object {$_.SwitchType -eq 'Internal'}
			$internalVMadapter = Get-VMNetworkAdapter -VMName $name | Where-Object {$_.SwitchId -eq $internalSwitch.Id}
			
			if(!$internalVMadapter){
				# Create the network adapter
				Add-VMNetworkAdapter -VMName $name -SwitchName $internalSwitch.Name -Name $internalSwitch.Name
				$internalVMadapter = Get-VMNetworkAdapter -VMName $name | Where-Object {$_.SwitchId -eq $internalSwitch.Id}
			}
			
			switch($internalvlantype){
				'Promiscuous' {
					$internalVMadapter | Set-VMNetworkAdapterVlan -Promiscuous -PrimaryVlanId $internalvlanprimary -SecondaryVlanIdList $internalvlansecondary
				}
				'Community' {
					$internalVMadapter | Set-VMNetworkAdapterVlan -Community -PrimaryVlanId $internalvlanprimary -SecondaryVlanId $internalvlansecondary
				}
				'Isolated' {					
					$internalVMadapter | Set-VMNetworkAdapterVlan -Isolated -PrimaryVlanId $internalvlanprimary -SecondaryVlanId $internalvlansecondary
				}
			}
		}
		
		# Configure external switches
		if($externalswitches){			
			# Loop on each switch corresponding to the specified argument
			foreach($curSwitchFilter in ($externalswitches -split ':')) {
				$switches | Where-Object { $_.SwitchType -ne 'Internal' -and $_.Name -like $curSwitchFilter } |% {
				
					# Create the network adapter
					Add-VMNetworkAdapter -VMName $name -SwitchName $_.NAme -Name $_.Name
				}
			}
		}
	}
	
	
	$result.changed = $true
}

# Remove the virtual machine
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
function Remove-VirtualMachine {

	# Get the VM object from Hyper-V
	$vm = Get-VM -Name $name

	# Remove all the snapshots
	$vm | Remove-VMSnapshot -IncludeAllChildSnapshots

	# Remove all the VHD
	Get-VHD -VMId $vm.Id |% {
		Remove-Item $_.path
	}

	# Remove the VM
	$vm | Remove-VM -Force
	
	$result.changed = $true
}

# Remove the virtual machine
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
function Start-VirtualMachine {
	$vm = Get-VM -Name $name
	if($vm -and $vm.state -ne 'Running') {
		# Start the VM object from Hyper-V
		Start-VM -Name $name

		$result.changed = $true
	}
}

# Remove the virtual machine
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
function Stop-VirtualMachine {
	$vm = Get-VM -Name $name
	if($vm -and $vm.state -eq 'Running') {
		# Stop the VM object from Hyper-V
		Stop-VM -Name $name

		$result.changed = $true
	}
}

# Get the virtual machine IP addresses
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
function Get-VirtualMachineIP {
	$psInfo = Get-VM -Name $name
	
	return $psInfo.NetworkAdapters | Where-Object { $_.IPAddresses } |% { $_.IPAddresses -match '.' }
}

try {
	if($gather_facts -eq 'yes'){

		Set-Attr $result "inventory" $null;
		$res = @()
		
		# get Hyper-V Switches
		$vmSwitches = Get-VMSwitch | Select-Object -Property Id,SwitchType
		$internalSwitches = $vmSwitches | Where-Object { $_.SwitchType -eq 'Internal' }
		$externalSwitches = $vmSwitches | Where-Object { $_.SwitchType -ne 'Internal' }
		
		# Get information from Hyper-V WMI database
		$hypervService = Get-WmiObject -Namespace "root\virtualization\v2" -query ("SELECT * FROM Msvm_VirtualSystemManagementService")
		$wmiInfo = $hypervService.GetSummaryInformation($null,(0..200)).SummaryInformation | Where-Object { $_.ElementName -like $Name }

		# Get information from Hyper-V Cmdlet
		$psInfo = Get-VM -Name $Name

		foreach($curWmiInfo in $wmiInfo) {
			$curPsInfo = $psInfo | Where-Object { $_.Name -eq $curWmiInfo.ElementName }
			
			switch ($Type) {
				'Connection' {
					$newObject = New-Object PSObject
					$newObject | Add-Member -MemberType NoteProperty -Name Name -Value $curWmiInfo.ElementName
					$newObject | Add-Member -MemberType NoteProperty -Name OperatingSystem -Value $curWmiInfo.GuestOperatingSystem
					$newObject | Add-Member -MemberType NoteProperty -Name OperatingSystemType -Value $( 
						if($curWmiInfo.GuestOperatingSystem -like '*windows*') {
							'windows'
						}
						else {
							'linux'
						}
					)
					$newObject | Add-Member -MemberType NoteProperty -Name IPAddress -Value $(
						$netAdapter = $curPsInfo.NetworkAdapters | Where-Object { $internalSwitches.Id -contains $_.SwitchId -and $_.IPAddresses } | Select-Object -First 1
						
						if(!$netAdapter) {
							$netAdapter = $curPsInfo.NetworkAdapters | Where-Object { $externalSwitches.Id -contains $_.SwitchId -and $_.IPAddresses } | Select-Object -First 1
						}
						
						if($netAdapter) {
							$netAdapter.IPAddresses -match '[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}' | Select-Object -First 1
						}
					)
					$newObject | Add-Member -MemberType NoteProperty -Name MacAddress -Value $(
						$netAdapter = $curPsInfo.NetworkAdapters | Where-Object { $internalSwitches.Id -contains $_.SwitchId -and $_.MacAddress } | Select-Object -First 1
						
						if(!$netAdapter) {
							$netAdapter = $curPsInfo.NetworkAdapters | Where-Object { $externalSwitches.Id -contains $_.SwitchId -and $_.MacAddress } | Select-Object -First 1
						}
						
						if($netAdapter) {
							($netAdapter.MacAddress | Select-Object -First 1) -replace '(..(?!$))','$1:'
						}
					)
					$res += @($newObject)
				}
				default {
					$curWmiInfo | gm -Type Property | Where-Object { $_.Name -notlike '__*' -and $_.Name -ne 'ProcessorLoadHistory' -and $_.Name -notlike 'ThumbnailImage*' } |% { $_.Name } |% {
						if(! ($psInfo | gm $_) ) {
							$curPsInfo | Add-Member -MemberType NoteProperty -Name $_ -Value $wmiInfo.$_ 
						}
					}
					$res += @($curPsInfo)
				}
			}
		}

		$result.inventory = $res
		
		echo $result | ConvertTo-Json -Compress -Depth 4

	}
	else {
		if([string]::IsNullOrEmpty($name) -or $name -eq '*') {
			Fail-Json $result "missing required argument: name"
		}
		elseif ('present','absent','restart','started','stopped' -notcontains $state) {
			Fail-Json $result "state is $state; must be present or absent"
		}
		elseif(!(Test-HyperVEnabled)) {
			Fail-Json $result 'Hyper-V feature is not enabled.'
		}
		
		switch ($state){
			'present' {
			
				if($template) {
					$templatefile = Get-ChildItem -recurse ('{0}\Templates\{1}.vhdx' -f (Get-VMHost).VirtualMachinePath, $template) | Select-Object -First 1
					if(!$templatefile) {
						Fail-Json $result "Unable to find a template nammed $template."
					}
				}
				
				if($internalswitch){
					if('yes','no' -notcontains $internalswitch) {
						Fail-Json $result "internalswitch is $internalswitch; must be yes or no"
					}
					elseif($internalvlantype -and 'Promiscuous','Community','Isolated' -notcontains $internalvlantype) {
						Fail-Json $result "internalvlantype is $internalvlantype; must be Promiscuous, Community or Isolated"
					}
				}
			
				if(!(Test-VirtualMachineExists)) {
					Create-VirtualMachine
				}
			}
			'absent' {
				if(Test-VirtualMachineExists) {
					Remove-VirtualMachine
				}
			}
			'started' {
				if(Test-VirtualMachineExists) {
					Start-VirtualMachine
					
					if($WaitForIPAddress -eq 'yes') {
						$ipaddresses = $null
						while(!$ipaddresses) {
							$ipaddresses = Get-VirtualMachineIP
						}
					}
				}
			}
			'stopped' {
				if(Test-VirtualMachineExists) {
					Stop-VirtualMachine
				}
			}
		}
		
		Exit-Json $result
	}
}
catch {
     Fail-Json $result $_.Exception.Message
}