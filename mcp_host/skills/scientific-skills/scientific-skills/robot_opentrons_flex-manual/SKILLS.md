

---
# Source: additional-documentation.md
---

---
title: "Opentrons Flex: Additional Documentation"
---

# Additional Documentation

Opentrons maintains additional online documentation for our hardware and software products. You may find these resources valuable as you use Opentrons Flex.

## Opentrons Knowledge Hub

The [Opentrons Knowledge Hub](https://opentrons.com/resources/knowledge-hub/) hosts publications about Opentrons products and related scientific applications. Some of the publication categories are:

- **Application Notes:** Scientific papers on performing particular applications with Opentrons hardware. Topics range from nucleic acid extraction and NGS quantification to handling volatile or viscous liquids.

- **Certificates:** Official regulatory and compliance documents for Opentrons hardware.

- **Documentation & Manuals:** Product instruction manuals (including this one) for Opentrons robots and modules. Also includes digital versions of the Quickstart Guides that ship in Opentrons product packages.

- **White Papers:** Documents that detail how Opentrons products are constructed and validated. White papers include dimensional drawings of Opentrons hardware.

## Python Protocol API documentation

The [online documentation for the Opentrons Python Protocol API](https://docs.opentrons.com/v2/) describes how to write automated biology lab protocols for Opentrons robots and hardware modules. The documentation includes a [Tutorial](https://docs.opentrons.com/v2/tutorial.html) for users writing their first Python protocol.

The Python API documentation covers writing Python code to:

- Load and work with labware.

- Load and work with Opentrons modules.

- Load and work with pipettes and the gripper.

- Perform discrete liquid-handling actions, such as aspirating and dispensing.

- Perform complex liquid-handling actions, such as transfers between wells.

- Move instruments to exact locations in the working area.

There is also a [Python API reference](https://docs.opentrons.com/v2/new_protocol_api.html) with information about all of the classes and methods that comprise the API.

## Opentrons HTTP API reference

The [Opentrons HTTP API reference](http://docs.opentrons.com/http/api_reference.html) describes all of the endpoints of the API used to directly control Opentrons robots. The API has many endpoint categories, including:

- Querying the state of the robot.

- Performing calibration tasks.

- Managing and running protocols.

- Moving the gantry and instruments.

- Controlling discrete systems like the ambient lighting and camera.

The API reference is defined by and generated from an [OpenAPI](https://www.openapis.org) specification.

## Developer documentation

Documentation for working directly with Opentrons source code is available alongside the corresponding code on GitHub. Notable documentation pages include:

- [Development Environment Setup](https://github.com/Opentrons/opentrons/blob/edge/DEV_SETUP.md): Opinionated instructions for setting up your computer to work on the software in the Opentrons/opentrons repository. These setup steps are required for running the Opentrons App or a simulated robot server from source.

- [Opentrons Emulation Wiki](https://github.com/Opentrons/opentrons-emulation/wiki): Explanation and instructions for using our software that emulates Opentrons robots at the firmware or hardware level.


---
# Source: glossary.md
---

---
title: "Opentrons Flex: Glossary"
---

# Glossary

This appendix defines terms related to Opentrons Flex. It omits industry-standard terms like "labware" unless the term has a special meaning in relation to Flex. For example, the definition for *pipette* describes the narrower meaning that the term has when using Flex, as opposed to any pipette you might find elsewhere in a lab.

The glossary is formatted to help you navigate within it and to other places in this manual. Words in italics indicate terms that are also defined in the glossary. Extremely common terms like "deck", "module", "pipette", and "protocol" aren't italicized, to improve readability. Links within definitions take you to the most relevant section that includes additional discussion of the term. And you can always use your PDF reader to search for every occurrence of a term to find even more information.

##### Above deck

Space that is on or above the level of the robot's deck area.

##### Aluminum block

See *thermal block*.

##### Ambient lighting

LEDs that illuminate the interior of Flex, which you can toggle on and off from the *touchscreen* or the *Opentrons App*.

##### Auxiliary ports

Ports on the back of the Flex labeled AUX-1 and AUX-2. The port connection type is an [IEC M12 metric screw connector](https://en.wikipedia.org/wiki/IEC_metric_screw_sized_connectors). See the [Connections section][connections] in the System Description chapter.

##### A1 expansion slot

The area of the deck behind slot A1. When its cover is removed, the A1 expansion slot provides enough space to install the Thermocycler Module. See the [Deck and working area section][deck-and-working-area] of the System Description chapter.

##### Below deck

The empty area below the robot's *deck slots*. This space provides clearance for module caddies that sit below the deck and allows for below-deck cable routing.

##### Caddy

See *module caddy*.

##### Calibration pin

A metal pin you attach to the *gripper's jaws* during gripper calibration. See the [Gripper calibration section][gripper-calibration] in the System Description chapter.

##### Calibration probe

A metal collar you attach to the *nozzle* of a pipette during pipette calibration, module calibration, and *Labware Position Check*. See the [Pipette calibration section][pipette-calibration] in the System Description chapter and the [Module calibration section][module-calibration] in the Modules chapter. See also the [Labware Position Check section](software-operation.md#labware-position-check) of the Software and Operation chapter.

##### Calibration square

The central part of a *removable deck slot* or *module calibration adapter*. The square is made of steel to reduce the chance of surface damage during calibration.

##### Camera

A built-in camera that provides an above-deck view inside the Flex enclosure.

##### Carrying handle

One of four aluminum handles that screw into the bottom corners of the robot. The handles help make Flex easier to lift. Lifting the robot requires two people. Using the handles is the best way to pick up Flex and move it.

##### Carrying handle cap

A flat metal cover that goes over the attachment point for a *carrying handle*. The caps close the handle openings in the *frame* and give the robot a clean appearance. See the [Physical components section][physical-components] in the System Description chapter.

##### Dashboard

The main screen for the robot, accessible by tapping the robot's name in the top left corner of the *touchscreen*. The dashboard gives you quick access to recently run protocols. See the [Touchscreen operation section][touchscreen-operation] in the Software and Operation chapter.

##### Deck

The machined aluminum surface on which automated science protocols are executed. It includes the *working area*, *staging area*, and *A1 expansion slot*. See the [Deck and working area section][deck-and-working-area] in the System Description chapter.

##### Deck border

The fixed portion of the deck around the four edges of the robot (outside of the area where *deck slot*

panels fit). It contains the removable accessory covers.

##### Deck fixture

Hardware items that replace standard *deck slots*. They let you customize the deck layout and

add functionality to your Flex. Deck fixtures include the *staging area slots*, *trash bin*, and *waste chute*.

##### Deck slot

A detachable panel on the deck area. Remove deck slots to install modules and for access to the space below the deck.

##### Ejector

The mechanism that automatically pushes tips off the *nozzle* of a pipette. See the [Pipettes section][pipettes] in the System Description chapter.

##### Emergency Stop Pendant

An external accessory that you press to stop the robot immediately. Also referred to as the E-stop. See the [Emergency Stop Pendant section](system-description.md#emergency-stop-pendant) in the System Description chapter.

##### Expansion slot

See *A1 expansion slot*.

##### Extension mount

The attachment point on the *gantry* for the Flex Gripper. See the [Movement system section][movement-system] in the System Description chapter.

##### Finishing cap

See *carrying handle cap*.

##### Firmware

The low-level software that controls the Flex robot and all of its peripheral systems. The Flex robot will automatically update the firmware on connected instruments and modules to stay in sync with the robot software version.

##### Fixture

See *deck fixture*.

##### Frame

The outer metal structure of the robot.

##### Front door

The hinged clear panel on the front of the robot.

##### Gantry

The robot's positioning system that moves attached *instruments* horizontally (on the x- and y-axis). See the [Movement system section][movement-system] in the System Description chapter.

##### Gripper

The Opentrons Flex Gripper, an *instrument* that picks up labware and moves it around the deck automatically.

##### Home gantry

The act of moving the *gantry* to a defined position at the back right of the *working area*.

##### Instrument

Any component that attaches to the *gantry* and manipulates liquids or labware on the deck. Examples include the 1- , 8- , and 96-channel pipettes, and the gripper.

##### Instrument mount

Attachment point for an *instrument*. Examples include the *pipette mounts* and the *extension mount* for the *gripper*. See the [Movement system section][movement-system] in the System Description chapter.

##### Jaws

The moving pincers of the *gripper*. See the [Gripper specifications section][gripper-specifications] in the System Description chapter.

##### JSON protocol

A standardized scientific procedure written as a [JavaScript object notation](https://en.wikipedia.org/wiki/JSON) file. The Opentrons *Protocol Designer* outputs JSON protocols.

##### JSON schema

A set of requirements for the structure and contents of a [JavaScript object notation](https://en.wikipedia.org/wiki/JSON) file. For example, all of the [Opentrons labware definitions](https://github.com/Opentrons/opentrons/tree/edge/shared-data/labware/definitions) are formatted according to a particular JSON schema, while *JSON protocols* follow another schema.

##### Labware clips

The plastic pieces at the corners of *deck slots*. Labware clips hold labware in place.

##### Labware Creator

The [Opentrons Labware Creator](https://labware.opentrons.com/create/) is a no-code, web-based tool that uses a graphical interface to help you create a labware definition file to import into the *Opentrons App*. After importing it, your custom labware is available to the Flex robot and the *Python Protocol API*.

##### Labware Library

The [Opentrons Labware Library](https://labware.opentrons.com/) lists the durable and consumable items you can use with the Flex by default, without customization. It includes things like well plates, reservoirs, tips, tip racks, and tubes.

##### Labware offset

Positional data that is created and stored by running *Labware Position Check*. Flex takes these offsets into account when moving to a particular type of labware in a particular *deck slot*.

##### Labware Position Check

A guided process to visually check and adjust pipette movement relative to a piece of labware, with a resolution of 0.1 mm. See the [Labware Position Check section](software-operation.md#labware-position-check) in the Software and Operation chapter.

##### Lift handles

See *carrying handles*.

##### Lights

See *ambient lighting* or *status light*.

##### Maintenance position

A specific *gantry* position at the front left side of the *working area*. The gantry moves to this position to facilitate adding or removing *instruments*.

##### Module

A peripheral that occupies a *deck slot*. Most modules are controlled by the robot via a USB connection. The Heater-Shaker, Temperature Module, and Thermocycler are all powered modules. The Magnetic Block is an unpowered module. See the [Modules chapter](modules.md).

##### Module caddy

A container that holds a module. It is used to attach modules to the deck area and help with module removal. Caddies place your labware closer to the deck surface and allow for below-deck cable routing.

##### Module calibration adapter

An adapter that sits on top of a module and is used to automatically calibrate module position.

##### Mounting plate

See *96-channel mounting plate*.

##### Nozzle

The working end of a pipette. Flex pipettes pick up disposable tips by pressing the nozzles down into them. See the [Pipettes section][pipettes] in the System Description chapter.

##### Opentrons App

Software used to control a Flex (or other Opentrons robots) from a laptop or desktop computer. The Opentrons App is available for Mac, Windows, and Linux. See the [Opentrons App section](software-operation.md#opentrons-app) in the Software and Operation chapter.

##### Paddle

Part of the *gripper* that grasps and holds labware. Paddles are replaceable wear items. See the [Gripper specifications section][gripper-specifications] in the System Description chapter.

##### Pinned protocol

Protocols you have saved for easy access at the top of the All Protocols tab on the *touchscreen*. See the [Protocol management section][protocol-management] in the Software and Operation chapter.

##### Pipette

[Opentrons Flex Pipettes](https://opentrons.com/products/categories/pipettes) are configurable devices used to move liquids throughout the *working area* during the execution of protocols. There are several Flex pipettes, which can handle volumes from 1 µL to 1000 µL in 1, 8, or 96 channels. See the [Pipettes section][pipettes] in the System Description chapter.

##### Pipette mount

The attachment point on the *gantry* for a pipette. See the [Movement system section][movement-system] in the System Description chapter.

##### Profile

See *Thermocycler profile*.

##### Protocol

An automated task or procedure you program to run on Opentrons robots, including Opentrons Flex. You can also search for, download, and use ready-made protocols from the Opentrons *Protocol Library*.

##### Protocol Designer

A web-based, no-code tool for developing *JSON protocols* that run on Opentrons robots, including Opentrons Flex. See the [Protocol Designer section](protocol-development.md#protocol-designer) in the Protocol Development chapter and <https://designer.opentrons.com>.

##### Protocol Library

A public, searchable library that hosts protocols authored by Opentrons or by members of the Opentrons community. See the [Protocol Library section](protocol-development.md#protocol-library) in the Protocol Development chapter and <https://library.opentrons.com>.

##### Protocol run

A particular instance of Flex performing the actions specified in a protocol file. Only a single protocol run can be active at any given time. Flex stores historical data on the time and outcome of the 20 most recent protocol runs.

##### Python protocol

A protocol script written using the Opentrons *Python Protocol API*. See the [Writing and running scripts section][writing-and-running-scripts] in the Protocol Development chapter.

##### Python Protocol API

A Python package that exposes a wide range of liquid handling features on Opentrons robots. See the [Python Protocol API section](protocol-development.md#python-protocol-api) in the Protocol Development chapter and the online [Opentrons Python Protocol API documentation](https://docs.opentrons.com/v2/).

##### Removable deck slot

See *deck slot*.

##### Run

See *protocol run*.

##### Side covers

Detachable panels on the side of the robot, used for module exhaust and external cable routing. See the [Connections section][connections] in the System Description chapter.

##### Side windows

Fixed clear panels on the right and left sides of the robot.

##### Staging area

The right-hand side of the *deck* (column 4), which is only accessible by the *gripper*. This area requires special *staging area slots* for use. See the [Staging area section](system-description.md#staging-area) in the System Description chapter.

##### Staging area slot

Staging area slots are ANSI/SLAS compatible deck pieces that replace the standard slots in column 3 (A3 to D3) and extend a new slot into the *staging area*. You can install a single slot or a maximum of four slots to create a new column (A4 to D4) along the right side of the *deck*. See the [Staging area section](system-description.md#staging-area) in the System Description chapter.

##### Status light

A strip of color LEDs along the top front of the robot. This light provides at-a-glance information about the robot. Different colors and patterns of illumination can communicate various success, failure, or idle states. See the [Touchscreen and LED displays section][touchscreen-and-led-displays] in the System Description chapter.

##### Thermal adapter

Aluminum blocks that attach to the Heater-Shaker and hold labware. See the [Thermal adapters section][thermal-adapters] in the Modules chapter.

##### Thermal block

Aluminum blocks that attach to the Temperature Module and hold labware to facilitate heating, cooling, and maintaining temperature. See the [Thermal blocks section][thermal-blocks] in the Modules chapter.

##### Thermocycler profile

A sequence of temperature changes used by the Thermocycler to perform heat-sensitive reactions. See the [Thermocycler profiles section][thermocycler-profiles] in the Modules chapter.

##### Tip rack adapter

An aluminum bracket used by the 96-channel pipette to attach a full rack of pipette tips. See the [Pipettes section][pipettes] in the System Description chapter.

##### Touchscreen

The interactive LCD screen mounted to the front of the robot. See the [Touchscreen and LED displays section][touchscreen-and-led-displays] in the System Description chapter.

##### Trash bin

A removable trash container. By default, it occupies slot A3 on the deck.

##### USB ports

Connections for Flex accessories, modules, and computers. See the [USB and auxiliary connections section][usb-and-auxiliary-connections] in the System Description chapter.

##### User Kit

A box that contains tools, fasteners, and spare parts. Every Flex robot ships with a User Kit.

##### Waste chute

A *deck fixture* that transfers liquids, tips, tip racks, and well plates from the Flex enclosure to a trash receptacle placed below its external opening.

##### Working area

The physical space above the deck that is accessible for pipetting. See the [Deck and working area section][deck-and-working-area] in the System Description chapter.

##### Workstation

Opentrons Flex workstations include the Flex robot, instruments, modules, accessories, and labware needed to automate a particular application. See the [Flex workstations section][flex-workstations] in the Introduction.

##### Z-axis carriage

The *gantry* component that includes the *pipette mounts* and the *extension mount* for the *gripper*. It moves these *instruments* along the z-axis (up and down) to locate them precisely during protocol execution. See the [Movement system section][movement-system] in the System Description chapter.

##### 96-channel mounting plate

A metal frame that mounts to the *z-axis carriage*. It holds the 96-channel pipette to the *gantry*.

## Network ports

Flex requires an internet connection for initial setup. After setup, it's possible to run Flex without a network connection, although some features of Flex and the Opentrons App expect local area network access over certain ports.

Network ports are software-defined connections between devices on a network. Each numbered port handles data for a specific network protocol or service. Flex uses these ports for services like software updates, file transfers, or to accept command-line instructions from a terminal.

The following table lists the network ports used by Flex, along with their function. All listed ports use TCP, except for port 5353, which uses UDP.

| Port number | Description |
| :---------- | :---------- |
| **22** | Used to make a Secure Shell (SSH) connection. See [Command-line operation over SSH][command-line-operation-over-ssh]. | **80** | Used for HTTP traffic. |
| **443** | Used for HTTPS traffic. The Opentrons App uses this port to check for and download software updates. |
| **1883** | Used for [MQTT messages](https://mqtt.org). Flex sends realtime notifications to the Opentrons App using MQTT. This reduces network traffic and shortens delays within the app, compared to polling. |
| **5353** | Used for Multicast DNS ([mDNS or zero-configuration networking](https://en.wikipedia.org/wiki/Zero-configuration_networking)). The Opentrons App relies on mDNS to find Flex robots on a network. |
| **31950** | Used by the robot server for [HTTP API commands](https://docs.opentrons.com/http/api_reference.html). |
| **48888** | Used for the built-in [Jupyter Notebook server][jupyter-notebook], which you can connect to with your web browser. |

If you're having trouble with these services, consult your facility's IT documentation or contact your IT manager for assistance with your network setup.

### Product elements

The Flex ships with the components listed below. Pipettes, the gripper, and modules come in separate packaging from the main Flex crate, even if you purchased them together as a workstation.

<div class="parts-list" markdown>

<figure markdown>
![Opentrons Flex robot](images/parts-list/flex-robot.svg "Opentrons Flex robot")
<figcaption>(1) Opentrons Flex robot</figcaption>
</figure>

<figure markdown>
![USB cable](images/parts-list/usb-cable.svg "USB cable")
<figcaption>(1) USB cable</figcaption>
</figure>

<figure markdown>
![Ethernet cable](images/parts-list/ethernet-cable.svg "Ethernet cable")
<figcaption>(1) Ethernet cable</figcaption>
</figure>

<figure markdown>
![Power cable](images/parts-list/power-cable.svg "Power cable")
<figcaption>(1) Power cable</figcaption>
</figure>

<figure markdown>
![L-keys](images/parts-list/l-keys.svg "L-keys")
<figcaption>(5) L-keys
<p class="part-info">(12 mm hex, 1.5 mm hex,<br />
2.5 mm hex, 3 mm hex,<br />
T10 Torx)</p></figcaption>
</figure>

<figure markdown>
![Emergency Stop Pendant](images/parts-list/emergency-stop.svg "Emergency Stop Pendant")
<figcaption>(1) Emergency Stop Pendant</figcaption>
</figure>

<figure markdown>
![Deck slot with labware clips](images/parts-list/deck-plate.svg "Deck slot with labware clips")
<figcaption>(1) Deck slot with labware clips</figcaption>
</figure>

<figure markdown>
![Spare labware clips](images/parts-list/labware-clips.svg "Spare labware clips")
<figcaption>(4) Spare labware clips</figcaption>
</figure>

<figure markdown>
![Pipette calibration probe](images/parts-list/calibration-probe.svg "Pipette calibration probe")
<figcaption>(1) Pipette calibration probe</figcaption>
</figure>

<figure markdown>
![Carrying handles and caps](images/parts-list/carrying-handles.svg "Carrying handles and caps")
<figcaption>(4) Carrying handles and caps</figcaption>
</figure>

<figure markdown>
![Top window panel](images/parts-list/top-window-panel.svg "Top window panel")
<figcaption>(1) Top window panel</figcaption>
</figure>

<figure markdown>
![Side window panels](images/parts-list/side-window-panels.svg "Side window panels")
<figcaption>(4) Side window panels</figcaption>
</figure>

<figure markdown>
![2.5 mm hex screwdriver](images/parts-list/2-5-mm-hex-screwdriver.svg "2.5 mm hex screwdriver")
<figcaption>(1) 2.5 mm hex screwdriver</figcaption>
</figure>

<figure markdown>
![19 mm wrench](images/parts-list/19-mm-wrench.svg "19 mm wrench")
<figcaption>(1) 19 mm wrench</figcaption>
</figure>

<figure markdown>
![Window screws](images/parts-list/window-screw.svg "Window screws")
<figcaption>(16 + spares) Window screws
<p class="part-info">(M4x8 mm flat head)</p>
</figcaption>
</figure>

<figure markdown>
![Spare deck slot screws](images/parts-list/deck-plate-screw.svg "Spare deck slot screws")
<figcaption>(10) Spare deck slot screws
<p class="part-info">(M4x10 mm socket head)</p>
</figcaption>
</figure>

<figure markdown>
![Spare deck clip screws](images/parts-list/deck-clip-screw.svg "Spare deck clip screws")
<figcaption>(12) Spare deck clip screws
<p class="part-info">(M3x6 mm socket head)</p>
</figcaption>
</figure>

</div>

## Power on

Instruction to the user if robot is not powered on.

When you power on Flex, the Opentrons logo will appear on the touchscreen. After a few moments, it will show the "Welcome to your Opentrons Flex" screen.

<figure class="screenshot" markdown>
![The Opentrons Flex welcome screen.](images/welcome-to-flex.png "Welcome to your Opentrons Flex!")
<figcaption>The Opentrons Flex welcome screen. You should only see this screen when you start your Flex for the first time.</<figcaption>
</figure>

### Connect to a network or computer

Instruction to the user if robot is not connected to the internet.

Follow the prompts on the touchscreen to get your robot connected so it can check for software updates and receive protocol files. There are three connection methods: Wi-Fi, Ethernet, and USB.

<figure class="screenshot" markdown>
![Network connection options.](images/choose-network-type.png "Network connection options")
<figcaption>Network connection options. You need to have internet connectivity to set up Flex.</figcaption>
</figure>

**Wi-Fi:** Use the touchscreen to connect to Wi-Fi networks that are secured with WPA2 Personal authentication (most networks that only require a password to join fall under this category).

!!! note 
    Flex does not support captive portals (networks that don't have a password but load a webpage to authenticate users after connecting).

You can also connect to an open Wi-Fi network, but this is not recommended.

!!! warning
    Connecting to an open Wi-Fi network will allow anyone in range of the network signal to control your Opentrons Flex robot without authentication.

If you need to connect to a Wi-Fi network that uses enterprise authentication (including "eduroam" and similar academic networks that require a username and password), first connect to the Opentrons App by Ethernet or USB to complete initial setup. Then connect to the enterprise Wi-Fi network in the networking settings for your Flex. To access the networking settings:

1.  Click **Devices** in the left sidebar of the Opentrons App.

2.  Click the three-dot menu (⋮) for your Flex and choose **Robot Settings**.

3.  Click the **Networking** tab.

Select your network from the dropdown menu or choose "Join other network..." and enter its SSID. Choose the enterprise authentication method that your network uses. The supported methods are:

- EAP-TTLS with TLS

- EAP-TTLS with MS-CHAP v2

- EAP-TTLS with MD5

- EAP-PEAP with MS-CHAP v2

- EAP-TLS

Each of these methods requires a username and password, and depending on your exact network configuration may require certificate files or other options. Consult your facility's IT documentation or contact your IT manager for details of your network setup.

**Ethernet:** Connect your robot to a network switch or hub with an Ethernet cable. You can also connect directly to the Ethernet port on your computer, starting in robot system version 7.1.0.

**USB:** Connect the provided USB A-to-B cable to the robot's USB-B port and an open port on your computer. Use a USB B-to-C cable or a USB A-to-C adapter if your computer does not have a USB-A port.

To proceed with setup, the connected computer must have the Opentrons App installed *and running*. For details on installing the Opentrons App, see the [App Installation section][app-installation] of the Software and Operation chapter.

---
# Source: introduction.md
---

---
title: "Opentrons Flex: Introduction"
---

# Introduction

This chapter introduces you to the Opentrons Flex ecosystem, including the overall system design and available workstation configurations. It also includes important compliance and safety information, which you should review before setting up your Opentrons Flex robot. For more details on the features of Opentrons Flex, see the [System Description chapter](system-description.md).

## Welcome to Opentrons Flex

Opentrons Flex is a liquid-handling robot designed for high throughput and complex workflows. The Flex robot is the base of a modular system that includes pipettes, a labware gripper, deck fixtures, on-deck modules, and labware — all of which you can swap out yourself. Flex is designed with a touchscreen so you can work with it directly at the lab bench, or you can control it from across your lab with the Opentrons App or our open-source APIs.

Flex workstations come with all of the equipment — robot, hardware, and labware — that you need to get started automating common lab tasks. For other applications, Opentrons Flex runs on fully open-source software and firmware, and is reagent- and labware-agnostic, giving you control over how you design and run your protocols.

### What's new in Flex

Opentrons Flex is part of the Opentrons liquid handler series of robots. Users of Opentrons Flex may be familiar with the Opentrons OT-2, our personal pipetting robot. Flex goes beyond the capabilities of OT-2 in several key areas, delivering higher throughput and walkaway time.

| Feature                     | Description                                                                                                                                                                                                                                                           |
| :-------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Pipette throughput** | Flex pipettes have 1, 8, or 96 channels. The 96-channel pipette operates on 12 times as many wells at once as the largest OT-2 pipette.                                                                                                                               |
| **Pipette and tip capacities** | Flex pipettes have larger volume ranges (1–50 µL, 5–1000 µL) and can all work with any volume of Opentrons Flex tips. This is an improvement over OT-2 pipettes, which have smaller ranges and must use tips with a matching volume range.                         |
| **Gripper** | The Opentrons Flex Gripper picks up and moves labware around the deck automatically, without user intervention. The gripper enables more complex workflows within a single protocol run.                                                                             |
| **Automated calibration** | Positional calibration of Flex pipettes and the gripper is fully automated. Press one button, and the instrument will move to precision-machined points on the deck to determine its exact position, saving that data for use in your protocols.                      |
| **Touchscreen** | Flex has its own touchscreen interface that lets you control it directly, in addition to using the Opentrons App. Use the touchscreen to start protocol runs, check job status, and change settings right on the robot.                                                 |
| **Module caddies** | Flex modules fit into caddies that occupy space below the deck. Caddies place your labware closer to the deck surface and allow for below-deck cable routing. Caddies enable even more module and labware configurations on the deck.                                  |
| **Deck slot coordinates** | Deck slots on Flex are numbered with a coordinate system (A1–D4) which is similar to how wells are numbered on labware.                                                                                                                                             |
| **Movable trash** | The trash bin can go in multiple deck locations on Flex. The default location (slot A3) is the recommended position. You can also use the gripper to dispose of trash in the optional waste chute.                                                                     |
| **Size and weight** | Flex is a bit bigger and much heavier than OT-2. Installation tasks on Flex require the assistance of a lab partner.                                                                                                                                                   |

A detailed [comparison of robot technical specifications](https://opentrons.com/products/robots/) is available on the Opentrons website.

Both Flex and OT-2 robots run on our open-source software, and the Opentrons App can control both types of robots at once. While OT-2 protocols can't be run directly on Flex, it's straightforward to adapt them (see the [OT-2 Protocols section][ot-2-python-protocols] of the Protocol Development chapter for details).

### Flex workstations

Opentrons Flex workstations include the Flex robot, accessories, pipettes and gripper, on-deck modules, and labware needed to automate a particular application. All workstation components are modular. If you need to change applications, you can add or swap in other Flex hardware and compatible consumables.

#### NGS Workstation

The Opentrons Flex NGS Workstation automates NGS library prep. It can automate pre-sequencing workflows using any leading reagent system, including fragmentation- and tagmentation-based library prep.

In addition to the Flex robot, the NGS Workstation includes:

- Gripper

- Choice of pipette configuration

    - Two 8-Channel Pipettes (1–50 µL and 5–1000 µL)
  
    - 96-Channel Pipette (5–1000 µL)

- Waste Chute

- Magnetic Block

- Temperature Module

- Thermocycler Module

- Labware kit with filter tips, microcentrifuge tubes, reservoirs, and PCR plates

#### PCR Workstation

The Opentrons Flex PCR Workstation automates PCR setup and thermocycling workflows for up to 96 samples. It can aliquot chilled reagents and samples into a 96-well PCR plate. With the addition of the automated Thermocycler Module, use the gripper to load the plate into the Thermocycler, and then run your chosen PCR program.

In addition to the Flex robot, the PCR Workstation includes:

- Gripper

- Choice of pipette configuration

    - 1-Channel Pipette (1–50 µL) and 8-Channel Pipette (1–50 µL)
  
    - 96-Channel Pipette (5–1000 µL)

- Waste Chute

- Temperature Module

- Labware kit with filter tips, microcentrifuge tubes, reservoirs, and PCR plates

#### Nucleic Acid Extraction Workstation

The Opentrons Flex Nucleic Acid Extraction Workstation automates DNA/RNA isolation and purification. It uses the Magnetic Block for separation of magnetic beads, and the Heater-Shaker for sample lysis and resuspension of magnetic beads.

In addition to the Flex robot, the Nucleic Acid Extraction Workstation includes:

- Gripper

- Choice of pipette configuration

    - 1-Channel Pipette (5–1000 µL) and 8-Channel Pipette (5–1000 µL)
  
    - 96-Channel Pipette (5–1000 µL)

- Waste Chute

- Magnetic Block

- Heater-Shaker Module

- Labware kit with filter tips, reservoirs, PCR plates, and deep well plates

#### Magnetic Bead Protein Purification Workstation

The Opentrons Flex Magnetic Bead Protein Purification Workstation automates small-scale protein purification and proteomics sample prep for up to 96 samples. It is compatible with many popular magnetic-bead-based reagents.

In addition to the Flex robot, the Protein Purification Workstation includes:

- Gripper

- Choice of pipette configuration

    - 1-Channel Pipette (5–1000 µL) and 8-Channel Pipette (5–1000 µL)
  
    - 96-Channel Pipette (5–1000 µL)

- Waste Chute

- Magnetic Block

- Heater-Shaker Module

- Labware kit with filter tips, reservoirs, PCR plates, and deep well plates

### Biological safety

Treat specimens and reagents containing materials taken from humans as potentially infectious agents. Opentrons recommends using safe laboratory procedures as explained in [*Biosafety in Microbiological and Biomedical Laboratories (BMBL) 6th Edition*](https://www.cdc.gov/labs/bmbl/).

Under normal circumstances, the Flex does not create detectable aerosols from source liquids. However, under certain conditions, it is possible to generate aerosols from source liquids. When operating with biosafety level 2 or greater source liquids, consider taking precautions against aerosol exposure, in accordance with your local regulatory bodies. To minimize the potential risk of aerosol exposure from the robot, ensure that you:

- Perform maintenance as described in the [Maintenance and Service chapter](maintenance-service.md).

- Properly install and secure all instrument covers, pipettes, modules, and labware.

- Use proper pipetting technique to aid in the mitigation of aerosols.

### Toxic fumes

If you're working with volatile solvents or toxic substances, use an efficient laboratory ventilation system to remove any vapors that may be produced.

### Flammable liquids

The Flex has not been evaluated for use with flammable liquids and should not be used with flammable liquids.

---
# Source: labware.md
---

---
title: "Opentrons Flex: Labware"
---

# Labware 

This chapter covers items in the [Opentrons Labware Library](https://labware.opentrons.com/) you can use with Opentrons Flex and the Opentrons Flex Gripper. It also covers custom labware and, for our power users, links labware components to their corresponding JSON file definitions. 

You can [purchase labware](https://opentrons.com/products/categories/tips-&-labware) from the original equipment manufacturers or from the Opentrons shop. And, Opentrons is always working to verify new labware definitions. See the Labware Library (linked above) for the latest listings. 

## Labware concepts 

Labware encompasses more than just the objects placed on the deck and used in a protocol. To help you understand Opentrons labware, let's examine this topic from three different perspectives. For the Opentrons Flex, labware includes items in our Labware Library, data that defines each piece of labware, and custom labware. 

### Labware as hardware 

The Labware Library includes everything you can use by default with Opentrons Flex. These are durable components and consumable items that you work with, reuse, or discard while running a protocol. You don't need to take any special steps to work with the items in the Labware Library. The Flex robot knows how to work with everything in the library automatically. 

### Labware as data 

Labware information is stored in Javascript object notation (JSON) files with .json file extensions. A JSON file includes spatial dimensions (length, width, height), volumetric capacity (µL, mL), and other metrics that define surface features, their shapes, and locations. When running a protocol, the Flex reads these .json files to know what labware is on the deck and how to work with it. 

### Custom labware 

Custom labware is labware that is not included in the Labware Library or is labware created by the [Custom Labware Creator](https://labware.opentrons.com/create/). However, sometimes the idea of custom labware comes burdened by notions of complexity, expense, or difficulty. But, custom labware shouldn't be hard to understand or create. 

Let's take a moment to unpack the concept of custom labware. 

As an example, the Opentrons Labware Library includes 96-well plates (200 µL) from Corning and Bio-Rad, but other manufacturers make these well plates too. And, thanks to commonly accepted industry standards, the differences among these ubiquitous lab items are minor. However, an ordinary 200 μL, 96-well plate from Stellar Scientific, Oxford Lab, or Krackeler Scientific (or any other supplier for that matter) is "custom labware" for the Flex because it isn't pre-defined in our Labware Library. Additionally, minor differences in labware dimensions can have a drastic impact on the success of your protocol run. For this reason, it's important to have an accurate labware definition for each labware you want to use in your protocol. 

Also, while custom labware could be an esoteric, one-off piece of kit, most of the time it's just the tips, plates, tubes, and racks used every day in labs all over the world. Again, the only difference between Opentrons labware and custom labware is the new item is not predefined in the software that powers the robot. The Flex can, and does, work with other basic labware items or something unique, but you need to record that item's characteristics in a labware definition JSON file and import that data into the Opentrons App. See the [Custom Labware Definitions section][custom-labware-definitions] below for more information. 

To sum up, labware includes:

- Everything in the Opentrons Labware Library. 
- Labware definitions: data in a JSON file that defines shapes, sizes, and capabilities of individual items like well plates, tips, reservoirs, etc. 
- Custom labware, which are items that aren't included in the Labware Library. 

After reviewing these important concepts, let's examine the categories and items in the Opentrons Labware Library. After that, we'll finish the chapter with an overview of the data components of a labware file and summarize the Opentrons features and services that help you create custom labware. 

## Reservoirs 

The Opentrons Flex works by default with the single- and multi-well reservoirs listed below. Using these reservoirs helps reduce your prep work burden because they're automation-ready right out of the box. Reservoir information is also available in the [Opentrons Labware Library](https://labware.opentrons.com/?category=reservoir). 

### Single-well reservoirs 

![Single-well reservoir labware.](images/labware-1-well-reservoir.png "Single-well reservoir")

| Manufacturer | Specifications | API load name             |
| :----------- | :------------- | :------------------------ |
| Agilent      | <ul><li>290 mL</li><li>V bottom</li></ul> | [`agilent_1_reservoir_290ml`](https://github.com/Opentrons/opentrons/blob/edge/shared-data/labware/definitions/2/agilent_1_reservoir_290ml/3.json) |
| Axygen       | <ul><li>90 mL</li><li>Flat bottom</li></ul> | [`axygen_1_reservoir_90ml`](https://github.com/Opentrons/opentrons/blob/edge/shared-data/labware/definitions/2/axygen_1_reservoir_90ml/1.json) |
| NEST         | <ul><li>195 mL</li><li>Flat bottom</li></ul> | [`nest_1_reservoir_195ml`](https://github.com/Opentrons/opentrons/blob/edge/shared-data/labware/definitions/2/nest_1_reservoir_195ml/1.json) |
| NEST         | <ul><li>290 mL</li><li>V bottom</li></ul> | [`nest_1_reservoir_290ml`](https://github.com/Opentrons/opentrons/blob/edge/shared-data/labware/definitions/2/nest_1_reservoir_290ml/3.json) |

### Multi-well reservoirs 

![12-well reservoir labware.](images/labware-12-well-reservoir.png "12-well reservoir")

| Manufacturer | Specifications | API load name            |
| :----------- | :------------- | :----------------------- |
| NEST         | <ul><li>12 wells</li><li>15 mL/well</li><li>V bottom</li></ul> | [`nest_12_reservoir_15ml`](https://github.com/Opentrons/opentrons/blob/edge/shared-data/labware/definitions/2/nest_12_reservoir_15ml/2.json) |
| USA Scientific | <ul><li>12 wells</li><li>22 mL/well</li><li>V bottom</li></ul> | [`usascientific_12_reservoir_22ml`](https://github.com/Opentrons/opentrons/blob/edge/shared-data/labware/definitions/2/usascientific_12_reservoir_22ml/1.json) |

### Reservoirs and API definitions 

The [Opentrons Labware Library](https://labware.opentrons.com/) defines the characteristics of the reservoirs listed above in separate JSON files. The robot and the Opentrons Python API rely on these JSON definitions to work with labware used by your protocols. For example, when working with the API, the `ProtocolContext.load_labware` function accepts these labware names as valid parameters in your code. Linked API load names connect to the reservoir labware definitions in the [Opentrons GitHub repository](https://github.com/Opentrons/opentrons). 

### Custom reservoir labware 

Try creating a custom labware definition with the [Opentrons Labware Creator](https://labware.opentrons.com/create/) if a reservoir you'd like to use isn't listed here. A custom definition combines all the dimensions, metadata, shapes, volumetric capacity, and other information in a JSON file. The Opentrons Flex needs this information to understand how to work with your custom labware. See the [Custom Labware Definitions section][custom-labware-definitions] for more information. 

## Well plates 

The Opentrons Flex works by default with well plates listed below. Using these well plates helps reduce your prep work burden because they're automation-ready right out of the box. Well plate information is also available in the [Opentrons Labware Library](https://labware.opentrons.com/?category=wellPlate). 

<figure class="side-by-side" markdown>
![24-well plate labware.](images/labware-24-well-plate.png "24-well plate")
![96-well deep well plate labware.](images/labware-96-deep-well-plate.png "96-well deep well plate")
</figure>

### 6-well plates 

| Manufacturer | Specifications | API load name |
| :----------- | :------------- | :---------------------------- |
| Corning | <ul><li>6 wells</li><li>16.8 mL/well</li><li>Circular wells, flat bottom</li></ul> | [`corning_6_wellplate_16.8ml_flat`](https://github.com/Opentrons/opentrons/blob/edge/shared-data/labware/definitions/2/corning_6_wellplate_16.8ml_flat/3.json) |

### 12-well plates 

| Manufacturer | Specifications | API load name |
| :----------- | :------------- | :---------------------------- |
| Corning | <ul><li>12 wells</li><li>6.9 mL/well</li><li>Circular wells, flat bottom</li></ul> | [`corning_12_wellplate_6.9ml_flat`](https://github.com/Opentrons/opentrons/blob/edge/shared-data/labware/definitions/2/corning_12_wellplate_6.9ml_flat/3.json) |

### 24-well plates 

| Manufacturer | Specifications | API load name |
| :----------- | :------------- | :----------------------------- |
| Corning | <ul><li>24 wells</li><li>3.4 mL/well</li><li>Circular wells, flat bottom</li></ul> | [`corning_24_wellplate_3.4ml_flat`](https://github.com/Opentrons/opentrons/blob/edge/shared-data/labware/definitions/2/corning_24_wellplate_3.4ml_flat/3.json) |

### 48-well plates 

| Manufacturer | Specifications | API load name |
| :----------- | :------------- | :----------------------------- |
| Corning | <ul><li>48 wells</li><li>1.6 mL/well</li><li>Circular wells, flat bottom</li></ul> | [`corning_48_wellplate_1.6ml_flat`](https://github.com/Opentrons/opentrons/blob/edge/shared-data/labware/definitions/2/corning_48_wellplate_1.6ml_flat/4.json) |

### 96-well plates 

| Manufacturer | Specifications | API load name |
| :-------------- | :------------- | :---------------------------------- |
| Bio-Rad | <ul><li>96 wells</li><li>200 µL/well</li><li>Circular wells, V bottom</li></ul> | [`biorad_96_wellplate_200ul_pcr`](https://github.com/Opentrons/opentrons/blob/edge/shared-data/labware/definitions/2/biorad_96_wellplate_200ul_pcr/3.json) |
| Corning | <ul><li>96 wells</li><li>360 µL/well</li><li>Circular wells, flat bottom</li></ul> | [`corning_96_wellplate_360ul_flat`](https://github.com/Opentrons/opentrons/blob/edge/shared-data/labware/definitions/2/corning_96_wellplate_360ul_flat/3.json) |
| NEST | <ul><li>96 wells</li><li>100 µL/well</li><li>Circular wells, V bottom</li><li>PCR full skirt</li></ul> | [`nest_96_wellplate_100ul_pcr_full_skirt`](https://github.com/Opentrons/opentrons/blob/edge/shared-data/labware/definitions/2/nest_96_wellplate_100ul_pcr_full_skirt/3.json) |
| NEST | <ul><li>96 wells</li><li>200 µL/well</li><li>Circular wells, flat bottom</li></ul> | [`nest_96_wellplate_200ul_flat`](https://github.com/Opentrons/opentrons/blob/edge/shared-data/labware/definitions/2/nest_96_wellplate_200ul_flat/3.json) |
| NEST | <ul><li>96 deep wells</li><li>2000 µL/well</li><li>Square wells, V bottom</li></ul> | [`nest_96_wellplate_2ml_deep`](https://github.com/Opentrons/opentrons/blob/edge/shared-data/labware/definitions/2/nest_96_wellplate_2ml_deep/3.json) |
| Opentrons | <ul><li>Tough 96 wells</li><li>200 µL/well</li><li>Circular wells, V bottom</li><li>PCR full skirt</li></ul> | [`opentrons_96_wellplate_200ul_pcr_full_skirt`](https://github.com/Opentrons/opentrons/blob/edge/shared-data/labware/definitions/2/opentrons_96_wellplate_200ul_pcr_full_skirt/3.json) |
| Thermo Scientific | <ul><li>Nunc 96 deep wells</li><li>1300 µL/well</li><li>Circular wells, U bottom</li></ul> | [`thermoscientificnunc_96_wellplate_1300ul`](https://github.com/Opentrons/opentrons/blob/edge/shared-data/labware/definitions/2/thermoscientificnunc_96_wellplate_1300ul/2.json) |
| Thermo Scientific | <ul><li>Nunc 96 deep wells</li><li>2000 µL/well</li><li>Circular wells, U bottom</li></ul> | [`thermoscientificnunc_96_wellplate_2000ul`](https://github.com/Opentrons/opentrons/blob/edge/shared-data/labware/definitions/2/thermoscientificnunc_96_wellplate_2000ul/2.json) |
| USA Scientific | <ul><li>96 deep wells</li><li>2.4 mL/well</li><li>Square wells, U bottom</li></ul> | [`usascientific_96_wellplate_2.4ml_deep`](https://github.com/Opentrons/opentrons/blob/edge/shared-data/labware/definitions/2/usascientific_96_wellplate_2.4ml_deep/2.json) |

### 384-well plates 

| Manufacturer | Specifications | API load name |
| :---------------- | :------------------------- | :--------------------------------- |
| Applied Biosystems | <ul><li>384 wells</li><li>40 µL/well</li><li>Circular wells, V bottom</li></ul> | [`appliedbiosystemsmicroamp_384_wellplate_40ul`](https://github.com/Opentrons/opentrons/blob/edge/shared-data/labware/definitions/2/appliedbiosystemsmicroamp_384_wellplate_40ul/2.json) |
| Bio-Rad | <ul><li>384 wells</li><li>50 µL/well</li><li>Circular wells, V bottom</li></ul> | [`biorad_384_wellplate_50ul`](https://github.com/Opentrons/opentrons/blob/edge/shared-data/labware/definitions/2/biorad_384_wellplate_50ul/3.json) |
| Corning | <ul><li>384 wells</li><li>112 µL/well</li><li>Square wells, flat bottom</li></ul> | [`corning_384_wellplate_112ul_flat`](https://github.com/Opentrons/opentrons/blob/edge/shared-data/labware/definitions/2/corning_384_wellplate_112ul_flat/4.json) |

### Well plate adapters 

The aluminum plates listed below are [thermal adapters][thermal-adapters] for the Opentrons Heater-Shaker GEN1 module. You can use these standalone adapter definitions to load Opentrons verified or custom labware on top of the Heater-Shaker. 

| Adapter type | API load name |
| :----------- | :------------ |
| Opentrons 96 Deep Well Heater-Shaker Adapter with NEST Deep Well Plate 2 mL | [`opentrons_96_deep_well_adapter_nest_wellplate_2ml_deep`](https://github.com/Opentrons/opentrons/blob/edge/shared-data/labware/definitions/2/opentrons_96_deep_well_adapter_nest_wellplate_2ml_deep/1.json) |
| Opentrons 96 Flat Bottom Heater-Shaker Adapter with NEST 96 Well Plate 200 µL Flat | [`opentrons_96_flat_bottom_adapter_nest_wellplate_200ul_flat`](https://github.com/Opentrons/opentrons/blob/edge/shared-data/labware/definitions/2/opentrons_96_flat_bottom_adapter_nest_wellplate_200ul_flat/1.json) |
| Opentrons 96 PCR Heater-Shaker Adapter with NEST Well Plate 100 μL | [`opentrons_96_pcr_adapter_nest_wellplate_100ul_pcr_full_skirt`](https://github.com/Opentrons/opentrons/blob/edge/shared-data/labware/definitions/2/opentrons_96_pcr_adapter_nest_wellplate_100ul_pcr_full_skirt/1.json) |
| Opentrons Universal Flat Heater-Shaker Adapter with Corning 384 Well Plate 112 µL Flat | [`opentrons_universal_flat_adapter_corning_384_wellplate_112ul_flat`](https://github.com/Opentrons/opentrons/blob/edge/shared-data/labware/definitions/2/opentrons_universal_flat_adapter_corning_384_wellplate_112ul_flat/1.json) |

You can purchase adapters directly from Opentrons: 

- [Universal Flat Adapter](https://opentrons.com/products/universal-flat-adapter/)
- [PCR Adapter](https://opentrons.com/products/pcr-adapter/)
- [Deep Well Adapter](https://opentrons.com/products/deep-well-adapter/)
- [96 Flat Bottom Adapter](https://opentrons.com/products/96-flat-bottom-adapter/)

!!! note
    Don't use a combined definition if you need to move labware onto or off of the Heater-Shaker during your protocol, either with the gripper or manually. Use a standalone adapter definition instead. 

| Adapter/labware combination | API load name |
| :-------------------------- | :------------ |
| Opentrons 96 Deep Well Heater-Shaker Adapter with NEST Deep Well Plate 2 mL | [`opentrons_96_deep_well_adapter_nest_wellplate_2ml_deep`](https://github.com/Opentrons/opentrons/blob/edge/shared-data/labware/definitions/2/opentrons_96_deep_well_adapter_nest_wellplate_2ml_deep/1.json)    |
| Opentrons 96 Flat Bottom Heater-Shaker Adapter with NEST 96 Well Plate 200 µL Flat | [`opentrons_96_flat_bottom_adapter_nest_wellplate_200ul_flat`](https://github.com/Opentrons/opentrons/blob/edge/shared-data/labware/definitions/2/opentrons_96_flat_bottom_adapter_nest_wellplate_200ul_flat/1.json) |
| Opentrons 96 PCR Heater-Shaker Adapter with NEST Well Plate 100 µL          | [`opentrons_96_pcr_adapter_nest_wellplate_100ul_pcr_full_skirt`](https://github.com/Opentrons/opentrons/blob/edge/shared-data/labware/definitions/2/opentrons_96_pcr_adapter_nest_wellplate_100ul_pcr_full_skirt/1.json) |
| Opentrons Universal Flat Heater-Shaker Adapter with Corning 384 Well Plate 112 µL Flat | [`opentrons_universal_flat_adapter_corning_384_wellplate_112ul_flat`](https://github.com/Opentrons/opentrons/blob/edge/shared-data/labware/definitions/2/opentrons_universal_flat_adapter_corning_384_wellplate_112ul_flat/1.json) |

Adapters can be purchased directly from Opentrons at [https://shop.opentrons.com](https://shop.opentrons.com). 

### Well plates and API definitions 

The [Opentrons Labware Library](https://labware.opentrons.com/) defines the characteristics of the well plates listed above in separate JSON files. The Flex robot and the Opentrons Python API rely on these JSON definitions to work with labware used by your protocols. For example, when working with the API, the `ProtocolContext.load_labware` function accepts these labware names as valid parameters in your code. Linked API load names connect to the well plate labware definitions in the [Opentrons GitHub repository](https://github.com/Opentrons/opentrons). 

### Custom well plate labware 

Try using the Opentrons Labware Creator to make a custom labware definition if a well plate you'd like to use isn't listed here. A custom definition combines all the dimensions, metadata, shapes, volumetric capacity, and other information in a JSON file. The Opentrons Flex reads this information to understand how to work with your custom labware. See the [Custom Labware Definitions section][custom-labware-definitions] for more information. 

## Tips and tip racks 

Opentrons Flex tips come in 50 µL, 200 µL, and 1000 µL sizes. These are clear, non-conducting polypropylene tips that are available with or without filters. They're packaged sterile in racks that hold 96 tips and are free of DNase, RNase, protease, pyrogens, human DNA, endotoxins, and PCR inhibitors. Racks also include lot numbers and expiration dates. 

Flex pipette tips work with all single- and multi-channel Opentrons Flex 50 µL and 1000 µL pipettes. While any Flex tip fits on any Flex pipette, you should always match the tip to a pipette of the same capacity or larger. For best performance, use the smallest tips that can hold the amount of liquid you need to aspirate. See [Pipette specifications][pipette-specifications] for examples. 

| Pipette capacity | Compatible tips             |
| :--------------- | :-------------------------- |
| 1–50 µL          | 50 µL tips only             |
| 5–1000 µL        | 50 μL, 200 μL, and 1000 µL tips |

### Tip racks 

Unfiltered and filtered tips are bundled into a rack that consists of a reusable base plate, a mid-plate that holds 96 tips, and a lid. 

| Tip rack by volume | API load name                         |
| :----------------- | :------------------------------------ |
| 50 μL              | <ul><li>Unfiltered: [`opentrons_flex_96_tiprack_50ul`](https://github.com/Opentrons/opentrons/blob/edge/shared-data/labware/definitions/2/opentrons_flex_96_tiprack_50ul/1.json)</li><li>Filtered: [`opentrons_flex_96_filtertiprack_50ul`](https://github.com/Opentrons/opentrons/blob/edge/shared-data/labware/definitions/2/opentrons_flex_96_filtertiprack_50ul/1.json)</li></ul> |
| 200 µL             | <ul><li>Unfiltered: [`opentrons_flex_96_tiprack_200ul`](https://github.com/Opentrons/opentrons/blob/edge/shared-data/labware/definitions/2/opentrons_flex_96_tiprack_200ul/1.json)</li><li>Filtered: [`opentrons_flex_96_filtertiprack_200ul`](https://github.com/Opentrons/opentrons/blob/edge/shared-data/labware/definitions/2/opentrons_flex_96_filtertiprack_200ul/1.json)</li></ul> |
| 1000 µL            | <ul><li>Unfiltered: [`opentrons_flex_96_tiprack_1000ul`](https://github.com/Opentrons/opentrons/blob/edge/shared-data/labware/definitions/2/opentrons_flex_96_tiprack_1000ul/1.json)</li><li>Filtered: [`opentrons_flex_96_filtertiprack_1000ul`](https://github.com/Opentrons/opentrons/blob/edge/shared-data/labware/definitions/2/opentrons_flex_96_filtertiprack_1000ul/1.json)</li></ul> |

To help with identification, the tip rack mid-plates are color coded based on tip size: 

- 50 µL: magenta 
- 200 µL: yellow 
- 1000 µL: blue 

![50 µL tip rack in magenta, 200 µL tip rack in yellow, and 1000 µL tip rack in blue.](images/labware-flex-tip-racks.png "Flex tip racks")

When ordering or reordering, tips and racks come in two different packaged configurations: 

- **Racks:** Consist of separately shrink-wrapped tip racks (base plate, mid-plate with tips, and lid). Racked configurations are best when cleanliness is paramount, to avoid cross-contamination, or when your protocols don't allow for base plate or component reuse. 
- **Refills:** Consist of one complete tip rack (base plate, mid plate with tips, and lid) and individual tip containers. Refill configurations are best when your protocols allow for base plate or component reuse. 

### Tip-pipette compatibility 

Flex pipette tips are designed for the Opentrons Flex pipettes. Flex tips are not backwards compatible with Opentrons OT-2 pipettes, nor can you use OT-2 tips on Flex pipettes. 

Other industry-standard tips may work with Flex pipettes, but this is not recommended. To ensure optimum performance, you should only use Opentrons Flex tips with Flex pipettes. 

### Tip rack adapter 

The 96-channel pipette requires an adapter to attach a full rack of tips properly. During the attachment procedure, the pipette moves over the adapter, lowers itself onto the mounting pins, and pulls tips onto the pipettes by lifting the adapter and tip rack. 

![The 96-channel tip rack adapter.](images/96-channel-tip-rack-adapter.png "96-channel tip rack adapter")

!!! note
    Only use the tip rack adapter when picking up a full rack of tips at once. Place tip racks directly on the deck when picking up fewer tips. 

!!! warning
    Pinch point hazard. Keep hands away from the tip rack adapter while the pipette is attaching pipette tips. 

| Adapter type | API load name |
| :------------------------------ | :-------------------------------- |
| Opentrons Flex 96 Tip Rack Adapter | [`opentrons_flex_96_tiprack_adapter`](https://github.com/Opentrons/opentrons/blob/edge/shared-data/labware/definitions/2/opentrons_flex_96_tiprack_adapter/1.json) |

The tip rack adapter is compatible with the Opentrons Flex Gripper. You can use the gripper to place fresh tip racks on the adapter or to pick up and move used tip racks into the waste chute. 

## Tubes and tube racks 

<figure class="side-by-side" markdown>
![Empty Opentrons tube rack.](images/labware-tube-rack.jpg "Tube rack")
![NEST tubes in two sizes.](images/labware-tubes.jpg "NEST tubes")
</figure>

The [Opentrons 4-in-1 Tube Rack system](https://opentrons.com/products/4-in-1-tube-rack-set) works with the Opentrons Flex by default. Using the 4-in-1 tube rack helps reduce your prep work burden because the combinations it provides are automation-ready right out of the box. More information is also available in the [Opentrons Labware Library](https://labware.opentrons.com/?category=tubeRack). 

### Tube and rack combinations 

The Opentrons 4-in-1 tube rack supports a wide variety of tube sizes, singly or in different size (volume) combinations. These include a: 

- 6-tube rack for 50 mL tubes (6 × 50 mL). 
- 10-tube combination rack for four 50 mL tubes and six 15 mL tubes (4 × 50 mL, 6 × 15 mL). 
- 15-tube rack for 15 mL tubes (15 × 15 mL). 
- 24-tube rack for 0.5 mL, 1.5 mL, or 2 mL tubes (24 × 0.5 mL, 1.5 mL, 2 mL). 

!!! note
    All tubes are cylindrical with V-shaped (conical) bottoms unless otherwise indicated. 

### 6-tube racks 

| Tube type         | API load name                          |
| :---------------- | :------------------------------------- |
| 6 Falcon 50 mL    | [`opentrons_6_tuberack_falcon_50ml_conical`](https://github.com/Opentrons/opentrons/blob/edge/shared-data/labware/definitions/2/opentrons_6_tuberack_falcon_50ml_conical/1.json) |
| 6 NEST 50 mL      | [`opentrons_6_tuberack_nest_50ml_conical`](https://github.com/Opentrons/opentrons/blob/edge/shared-data/labware/definitions/2/opentrons_6_tuberack_nest_50ml_conical/1.json) |

### 10-tube racks 

| Tube type | API load name |
| :-------- | :------------ |
| <ul><li>4 Falcon 50 mL</li><li>6 Falcon 15 mL</li></ul> | [`opentrons_10_tuberack_falcon_4x50ml_6x15ml_conical`](https://github.com/Opentrons/opentrons/blob/edge/shared-data/labware/definitions/2/opentrons_10_tuberack_falcon_4x50ml_6x15ml_conical/1.json) |
| <ul><li>4 NEST 50 mL</li><li>6 NEST 15 mL</li></ul> | [`opentrons_10_tuberack_nest_4x50ml_6x15ml_conical`](https://github.com/Opentrons/opentrons/blob/edge/shared-data/labware/definitions/2/opentrons_10_tuberack_nest_4x50ml_6x15ml_conical/1.json) |

### 15-tube racks 

| Tube type          | API load name                           |
| :----------------- | :-------------------------------------- |
| 15 Falcon 15 mL    | [`opentrons_15_tuberack_falcon_15ml_conical`](https://github.com/Opentrons/opentrons/blob/edge/shared-data/labware/definitions/2/opentrons_15_tuberack_falcon_15ml_conical/1.json) |
| 15 NEST 15 mL      | [`opentrons_15_tuberack_nest_15ml_conical`](https://github.com/Opentrons/opentrons/blob/edge/shared-data/labware/definitions/2/opentrons_15_tuberack_nest_15ml_conical/1.json) |

### 24-tube racks 

| Tube type          | API load name                           |
| :----------------- | :-------------------------------------- |
| 24 Eppendorf Safe-Lock 1.5 mL   | [`opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap`](https://github.com/Opentrons/opentrons/blob/edge/shared-data/labware/definitions/2/opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap/1.json) |
| 24 Eppendorf Safe-Lock 2 mL, U-shaped bottom | [`opentrons_24_tuberack_eppendorf_2ml_safelock_snapcap`](https://github.com/Opentrons/opentrons/blob/edge/shared-data/labware/definitions/2/opentrons_24_tuberack_eppendorf_2ml_safelock_snapcap/1.json) |
| 24 generic 2 mL screw cap       | [`opentrons_24_tuberack_generic_2ml_screwcap`](https://github.com/Opentrons/opentrons/blob/edge/shared-data/labware/definitions/2/opentrons_24_tuberack_generic_2ml_screwcap/1.json)        |
| 24 NEST 0.5 mL screw cap        | [`opentrons_24_tuberack_nest_0.5ml_screwcap`](https://github.com/Opentrons/opentrons/blob/edge/shared-data/labware/definitions/2/opentrons_24_tuberack_nest_0.5ml_screwcap/1.json)         |
| 24 NEST 1.5 mL screw cap        | [`opentrons_24_tuberack_nest_1.5ml_screwcap`](https://github.com/Opentrons/opentrons/blob/edge/shared-data/labware/definitions/2/opentrons_24_tuberack_nest_1.5ml_screwcap/1.json)         |
| 24 NEST 1.5 mL snap cap         | [`opentrons_24_tuberack_nest_1.5ml_snapcap`](https://github.com/Opentrons/opentrons/blob/edge/shared-data/labware/definitions/2/opentrons_24_tuberack_nest_1.5ml_snapcap/1.json)          |
| 24 NEST 2 mL screw cap          | [`opentrons_24_tuberack_nest_2ml_screwcap`](https://github.com/Opentrons/opentrons/blob/edge/shared-data/labware/definitions/2/opentrons_24_tuberack_nest_2ml_screwcap/1.json)           |
| 24 NEST 2 mL snap cap, U-shaped bottom | [`opentrons_24_tuberack_nest_2ml_snapcap`](https://github.com/Opentrons/opentrons/blob/edge/shared-data/labware/definitions/2/opentrons_24_tuberack_nest_2ml_snapcap/1.json)          |

### Tube rack API definitions 

The [Opentrons Labware Library](https://labware.opentrons.com/) defines the characteristics of the tube racks listed above in separate JSON files. The Flex robot and the Opentrons Python API rely on these JSON definitions to work with labware used by your protocols. For example, when working with the API, the `ProtocolContext.load_labware` function accepts these labware names as valid parameters in your code. Linked API load names connect to the tube rack labware definitions in the [Opentrons GitHub repository](https://github.com/Opentrons/opentrons). 

### Custom tube rack labware 

Try creating a custom labware definition using the [Opentrons Labware Creator](https://labware.opentrons.com/create/) if a tube and rack combination you'd like to use isn't listed here. A custom definition combines all the dimensions, metadata, shapes, volumetric capacity, and other information in a JSON file. The Opentrons Flex reads this information to understand how to work with your custom labware. See the [Custom Labware Definitions section][custom-labware-definitions] for more information. 

## Aluminum blocks 

Aluminum blocks ship with the Temperature Module GEN2 and can be purchased separately as a [three-piece set](https://opentrons.com/products/aluminum-block-1-5-2-0ml-tubes). The set includes a flat bottom plate, a 24-well block, and a 96-well block. 

The Opentrons Flex uses aluminum blocks to hold sample tubes and well plates on the Temperature Module or directly on the deck. When used with the Temperature Module, the aluminum blocks can keep your sample tubes, PCR strips, or plates at a constant temperature between 4 °C and 95 °C. 

### Flat bottom plate 

The flat bottom plate for Flex ships with the Temperature Module's caddy and is compatible with various ANSI/SLAS standard well plates. This flat plate differs from the plate that ships with the Temperature Module itself or the separate three-piece set. It features a wider working surface and chamfered corner clips. These features help improve the performance of the Opentrons Flex Gripper when moving labware onto or off of the plate. 

You can tell which flat bottom plate you have because the one for Flex has the words "Opentrons Flex" on its top surface. The one for OT-2 does not. 

![The flat bottom plate with the Opentrons Flex logo.](images/temperature-module-block-flat.png "Flex flat bottom plate")

### 24-well aluminum block 

The 24-well block is used with individual sample vials. For example, it accepts sample vials that: 

- Have V-shaped or U-shaped bottoms. 
- Secure contents with snap cap or screw cap closures. 
- Hold liquid in capacities of 0.5 mL, 1.5 mL, and 2 mL. 

![24-well aluminum block adapter.](images/labware-24-well-block.jpg "24-well block")

### 96-well aluminum block 

The 96-well block supports a wide variety of well plate types. For example, it accepts well plates that are: 

- From major well-plate manufacturers like Bio-Rad and NEST. 
- Designed with V-shaped bottoms, U-shaped bottoms, or flat bottoms. 
- Designed with 100 µL or 200 µL wells. 

It is also compatible with generic PCR strips. 

![96-well aluminum block adapter.](images/labware-96-well-block.jpg "96-well block")

### Standalone adapters 

| Thermal block           | API load name                         |
| :---------------------- | :------------------------------------ |
| Flex flat bottom plate  | [`opentrons_aluminum_flat_bottom_plate`](https://github.com/Opentrons/opentrons/blob/edge/shared-data/labware/definitions/2/opentrons_aluminum_flat_bottom_plate/1.json)  |
| 24-well aluminum block  | *See labware combinations below.*     |
| 96-well aluminum block  | [`opentrons_96_well_aluminum_block`](https://github.com/Opentrons/opentrons/blob/edge/shared-data/labware/definitions/2/opentrons_96_well_aluminum_block/1.json)      |

### Aluminum block labware combinations 

The [Opentrons Labware Library](https://labware.opentrons.com/) supports the following block, vial, and well plate combinations, which are also defined in separate JSON labware definition files. The Flex robot and the Opentrons Python API rely on these JSON definitions to work with labware used by your protocols. For example, when working with the API, the `ProtocolContext.load_labware` function accepts these labware names as valid parameters in your code. The tables below list the default block/container combinations and related API load names. Links connect to corresponding JSON definitions in the [Opentrons GitHub repository](https://github.com/Opentrons/opentrons). 

!!! note
    All tubes have V-shaped bottoms unless otherwise indicated. 

### 24-well aluminum block labware combinations 

| 24-well block contents                | API load name                                   |
| :------------------------------------ | :---------------------------------------------- |
| Generic 2 mL screw cap                | [`opentrons_24_aluminumblock_generic_2ml_screwcap`](https://github.com/Opentrons/opentrons/blob/edge/shared-data/labware/definitions/2/opentrons_24_aluminumblock_generic_2ml_screwcap/1.json) |
| NEST 0.5 mL screw cap                 | [`opentrons_24_aluminumblock_nest_0.5ml_screwcap`](https://github.com/Opentrons/opentrons/blob/edge/shared-data/labware/definitions/2/opentrons_24_aluminumblock_nest_0.5ml_screwcap/1.json)  |
| NEST 1.5 mL screw cap                 | [`opentrons_24_aluminumblock_nest_1.5ml_screwcap`](https://github.com/Opentrons/opentrons/blob/edge/shared-data/labware/definitions/2/opentrons_24_aluminumblock_nest_1.5ml_screwcap/1.json)  |
| NEST 1.5 mL snap cap                  | [`opentrons_24_aluminumblock_nest_1.5ml_snapcap`](https://github.com/Opentrons/opentrons/blob/edge/shared-data/labware/definitions/2/opentrons_24_aluminumblock_nest_1.5ml_snapcap/1.json)   |
| NEST 2 mL screw cap                   | [`opentrons_24_aluminumblock_nest_2ml_screwcap`](https://github.com/Opentrons/opentrons/blob/edge/shared-data/labware/definitions/2/opentrons_24_aluminumblock_nest_2ml_screwcap/1.json)    |
| NEST 2 mL snap cap, U-shaped bottom   | [`opentrons_24_aluminumblock_nest_2ml_snapcap`](https://github.com/Opentrons/opentrons/blob/edge/shared-data/labware/definitions/2/opentrons_24_aluminumblock_nest_2ml_snapcap/1.json)     |

### 96-well aluminum block labware combinations 

| 96-well block contents      | API load name                                       |
| :-------------------------- | :-------------------------------------------------- |
| Bio-Rad well plate 200 µL   | [`opentrons_96_aluminumblock_biorad_wellplate_200uL`](https://github.com/Opentrons/opentrons/blob/edge/shared-data/labware/definitions/2/opentrons_96_aluminumblock_biorad_wellplate_200ul/1.json)   |
| Generic PCR strip 200 µL    | [`opentrons_96_aluminumblock_generic_pcr_strip_200uL`](https://github.com/Opentrons/opentrons/blob/edge/shared-data/labware/definitions/2/opentrons_96_aluminumblock_generic_pcr_strip_200ul/1.json)  |
| NEST well plate 100 µL      | [`opentrons_96_aluminumblock_nest_wellplate_100uL`](https://github.com/Opentrons/opentrons/blob/edge/shared-data/labware/definitions/2/opentrons_96_aluminumblock_nest_wellplate_100ul/1.json)     |

## Labware and the Opentrons Flex Gripper 

Although the Opentrons Flex works with all the inventory in the Labware Library, the Opentrons Flex Gripper is compatible with specific labware items only. Currently, the Gripper is optimized for use with the following labware items. 

| Labware category                | Brands                                     |
| :------------------------------ | :----------------------------------------- |
| Deep Well Plates                | <ul><li>NEST 96 Deep Well Plate 2 mL</li></ul> |
| Fully Skirted 96 Well Plates    | <ul><li>Opentrons Tough 96 Well Plate 200 µL PCR Full Skirt</li><li>NEST 96 Well Plate 200 µL Flat</li></ul> |
| Tip Racks (unfiltered and filtered tips) | <ul><li>Opentrons Flex 96 Tip Rack 50 µL</li><li>Opentrons Flex 96 Tip Rack 200 µL</li><li>Opentrons Flex 96 Tip Rack 1000 µL</li></ul> |

!!! note
    For best results, use the Flex Gripper only with the labware listed above. The Flex Gripper may work with other ANSI/SLAS automation compliant labware, but this is not recommended. 

## Custom labware definitions 

As discussed at the beginning of this chapter, custom labware is labware that's not listed in the Opentrons Labware Library. You can use other common or unique labware items with the Flex by accurately measuring and recording the characteristics of that object and saving that data in a JSON file. When imported into the app, the Flex and the API uses that JSON data to interact with your labware. Opentrons provides tools and services, which we'll examine below, to help you use the Flex with custom labware. 

### Creating custom labware definitions 

Opentrons tools and services help put custom labware within your reach. These features accommodate different skill levels and ways of working. Creating your own labware, and using it with the Opentrons Flex, helps make the robot a versatile and powerful addition to your lab. 

#### Custom Labware Creator 

The [Custom Labware Creator](https://labware.opentrons.com/create/) is a no-code, web-based tool that uses a graphical interface to help you create a labware definition file. Labware Creator produces a JSON labware definition file that you import into the Opentrons App. After that, your custom labware is available to the Flex robot and the Python API. 

#### Custom Labware Service 

Get in touch with us if the labware you'd like to use isn't available in the library, if you can't create your own definitions, or because a custom item includes different shapes, sizes, or other irregularities described below. 

| Labware you can define in Labware Creator | Labware Opentrons needs to define |
| :---------------------------------------- | :-------------------------------- |
| :material-checkbox-outline: Wells and tubes are uniform and identical. | :material-checkbox-outline: Wells and tube shapes vary.               |
| :material-checkbox-outline: All rows are evenly spaced (the space between rows is equal). | :material-checkbox-outline: Rows are not evenly spaced.               |
| :material-checkbox-outline: All columns are evenly spaced (the space between columns is equal). | :material-checkbox-outline: Columns are not evenly spaced.            |
| :material-checkbox-outline: Fits perfectly in one deck slot.       | :material-checkbox-outline: Smaller than one deck slot (requires adapter) or spans multiple deck slots. |

Here are some diagrams that help you visualize the examples described above. 

| Layout {style="width: 200px;"} | Description |
| ------ | ----------- |
| ![Labware with 3 evenly spaced rows and 4 evenly spaced columns.](images/labware-layout-regular-even-space.svg "Regular labware layout") | :material-check-bold:{ .opentrons-blue } **Regular** <br />All columns are evenly spaced and all rows are evenly spaced.<br />Columns do not need to have the same spacing as rows. |
| ![Labware with 3 evenly spaced rows and 4 evenly spaced columns on the left side of the labware.](images/labware-layout-regular-off-center.svg "Regular labware layout") | :material-check-bold:{ .opentrons-blue } **Regular** <br />The grid does not have to be in the center of labware.  |
| ![Labware with 4 columns of 3 rows, separated into two groups.](images/labware-layout-irregular-uneven-space.svg "Regular labware layout") | :octicons-x-12:{ .grey } **Irregular** <br />Rows are evenly spaced but **columns are not evenly spaced.**  |
| ![Labware with 3 square wells and 9 circular wells.](images/labware-layout-irregular-wells-not-identical.svg "Regular labware layout") | :octicons-x-12:{ .grey } **Irregular** <br />Columns/rows are evenly spaced but **wells are not identical.** |
| ![Labware with a 4-by-5 grid of wells and another 2-by-3 grid of wells.](images/labware-layout-irregular-multiple-grids.svg "Regular labware layout") | :octicons-x-12:{ .grey } **Irregular** <br />There is **more than one grid.** |

If you need help creating custom labware definitions, contact Opentrons Support (<support@opentrons.com>). They will work to design custom labware definitions based on your requirements. This is a fee-based service.

#### Python API 

While you cannot create custom labware with our API, you can use custom labware with the available API methods. However, you need to define your custom labware first and import it into the Opentrons App. 

Once you have added your labware to the Opentrons App, it's available to the Python API and the robot. For information about writing protocol scripts with the API, see the [Python Protocol API section](protocol-development.md#python-protocol-api) in the Protocol Development chapter. 

### JSON labware schema 

A JSON file is the blueprint for Opentrons standard and custom labware. This file contains and organizes labware data according to the design specifications set by the default schema. 

A schema is a framework for organizing data. It sets the rules about what information is required or optional and how it’s organized in the JSON file. If you’re interested, take a moment to review [our labware schema](https://github.com/Opentrons/opentrons/blob/edge/shared-data/labware/schemas). For an actual example, see the definition for the [Opentrons 96 PCR Adapter](https://github.com/Opentrons/opentrons/blob/edge/shared-data/labware/definitions/2/opentrons_96_pcr_adapter/1.json). The following table lists and defines the items in the Opentrons labware schema.

| Property {style="width: 20%;"} | Data type | Definition                                   |
| :------------------ | :-------- | :------------------------------------------- |
| `schemaVersion`     | Number    | Schema version used by a labware. The current version is `3`. |
| `version`           | Integer   | An incrementing integer that identifies the labware version. Minimum version is `1`. |
| `namespace`         | String    | See `safeString` in the JSON definitions section below. |
| `metadata`          | Object    | Properties used for search and display. Accepts only:<ul><li>`displayName` (String): An easy-to-remember labware name.</li><li>`displayCategory`: Labels used in the UI to categorize labware. See `displayCategory` in the JSON definitions section below.</li><li>`displayVolumeUnits` (String): Labels used in the UI to indicate volume. Must be either µL, mL, or L.</li></ul> |
| `brand`             | Object    | Information about the labware manufacturer or those products the labware is compatible with. |
| `parameters`        | Object    | Internal parameters that describe labware characteristics. Accepts only:<ul><li>`format` (String): Determines labware compatibility with multichannel pipettes. Must be one of `96Standard`, `384Standard`, `trough`, `irregular`, or `trash`.</li><li>`quirks` (Array): Strings describing labware behavior. See the [Opentrons 96 Deep Well Adapter](https://github.com/Opentrons/opentrons/blob/03cd0336c6051c05fa66088fabec426c7b751a85/shared-data/labware/definitions/2/opentrons_96_deep_well_adapter_nest_wellplate_2ml_deep/1.json#L1108) definition.</li><li>`isTiprack` (Boolean): Indicates if labware is a tip rack (`true`) or not (`false`).</li><li>`tipLength` (Number): Required if labware is a tip rack. Specifies tip length (in mm), from top to bottom, as indicated in technical drawings or as measured with calipers.</li><li>`tipoverlap` (Number): Required if labware is a tip rack. Specifies how far tips on a tip rack are expected to overlap with the pipette's nozzle. Defined as tip length minus the distance between the bottom of the pipette and the bottom of the tip. The robot's calibration process may fine-tune this estimate.</li><li>`loadName`: Name used to reference a labware definition (e.g., `opentrons_flex_96_tiprack_50_ul`).</li><li>`isMagneticModuleCompatible` (Boolean): Indicates if labware is compatible with the Magnetic Module.</li><li>`magneticModuleEngageHeight`: How far the Magnetic Module will move its magnets when used with this labware. See `positiveNumber` in the JSON definitions section below.</li></ul> |
| `ordering`          | Array     | An array that tracks how wells should be ordered on a piece of labware. See the [Opentrons 96 PCR Adapter](https://github.com/Opentrons/opentrons/blob/8569e32d2d918abb1f232f48a7b28385021215fd/shared-data/labware/definitions/2/opentrons_96_pcr_adapter/1.json#L2) example. |
| `cornerOffsetFromSlot` | Object    | Used for labware that spans multiple deck slots. Offset is the distance from the left-front-bottom corner of the slot to the left-front-bottom corner of the labware bounding box. Accepts only:<ul><li>`x` (number)</li><li>`y` (number)</li><li>`z` (number)</li></ul> For labware that does not span multiple slots, these values should be zero. See `positiveNumber` in the JSON definitions section below. |
| `dimensions`        | Object    | Outer dimensions (in mm) of a piece of labware. Accepts only:<ul><li>`xDimension` (length)</li><li>`yDimension` (width)</li><li>`zDimension` (height)</li></ul> See the [Opentrons 96 PCR Adapter](https://github.com/Opentrons/opentrons/blob/8569e32d2d918abb1f232f48a7b28385021215fd/shared-data/labware/definitions/2/opentrons_96_pcr_adapter/1.json#L26) example. |
| `wells`             | Object    | An unordered object of well objects, including position and dimensions.<br />Each well object's key is the well's coordinates, which must be an uppercase letter followed by a number, e.g., A1, B1, H12.<br />Each well object accepts the following properties:<ul><li>`depth` (Number): The distance (in mm) between the top and bottom of the well. For tip racks, depth is ignored in favor of `tipLength`, but the values should match.</li><li>`x` (Number): Location of the center-bottom of a well in reference to the left of the labware.</li><li>`y` (Number): Location of the center-bottom of a well in reference to the front of the labware.</li><li>`z` (Number): Location of the center-bottom of a well in reference to the bottom of the labware.</li><li>`totalLiquidVolume` (Number): Total well, tube, or tip volume in µL.</li><li>`xDimension` (Number): Length of a rectangular well.</li><li>`yDimension` (Number): Width of a rectangular well.</li><li>`diameter` (Number): Diameter of a circular well.</li><li>`shape` (String): Either `rectangular` or `circular`.<br />If `rectangular`, specify `xDimension` and `yDimension`.<br />If `circular`, specify `diameter`.</li></ul>For a circular well example, see the [Opentrons 96 PCR Adapter](https://github.com/Opentrons/opentrons/blob/8569e32d2d918abb1f232f48a7b28385021215fd/shared-data/labware/definitions/2/opentrons_96_pcr_adapter/1.json#L31). For a rectangular well example, see the [NEST 96 Deep Well Plate 2mL](https://github.com/Opentrons/opentrons/blob/8569e32d2d918abb1f232f48a7b28385021215fd/shared-data/labware/definitions/2/nest_96_wellplate_2ml_deep/2.json#L35).<br />For dimension, depth, and volume, see `positiveNumber` in the JSON definitions section below. |
| `groups`            | Array     | Logical well groupings for metadata and display purposes. Changes in groups do not affect protocol execution. Each item in the array accepts: <ul><li>`wells` (Array): An array of wells (e.g., `["A1", "B1", "C1"]`) that share the same metadata. Array elements are strings.</li><li>`metadata` (Object): Metadata specific to a grid of wells. Accepts only:</li><ul><li>`displayName` (String): Human-readable name for the well group.</li><li>`displayCategory`: Labels used to categorize well groups. See `displayCategory` in the JSON definitions section below.</li><li>`wellBottomShape` (String): Bottom shape of a well. Available shapes are `flat`, `u`, or `v` only.</li></ul><li>`brand`: Brand information for the well group. See `brandData` in the JSON definitions section below.</li></ul> |
| `allowedRoles`      | Array     | Defines an item's role or purpose. If the `allowedRoles` field is missing from a definition, an item is treated as `labware`. Possible array items are only the following strings: <ul><li>`labware` (standard labware items)</li><li>`adapter` (items designed to hold labware)</li><li>`fixture` (items that are affixed to the deck)</li><li>`maintenance` (items not used in normal protocol runs)</li></ul> |
| `stackingOffsetWithLabware` | Object    | For labware that can stack on top of another piece of labware. Used to determine z-height (labware z height + adapter z height - overlap). See `coordinates` in the JSON definitions section below. |
| `stackingOffsetWithModule` | Object    | For labware that can stack on top of a module. Used to determine z-height (module labware offset z + labware z - overlap). See `coordinates` in the JSON definitions section below. |
| `gripperOffsets`    | Object    | Offsets added when calculating the coordinates the gripper should go to when picking up or dropping other labware on this labware. Includes a `default` object that includes two properties: <ul><li>`pickUpOffset`: Offset added to calculate the pick-up coordinates of labware placed on this labware.</li><li>`dropOffset`: Offset added to calculate the drop-off coordinates of labware placed on this labware.</li></ul> See `coordinates` in the JSON definitions section below. |
| `gripForce`         | Number    | Measured in newtons, this is the force which the gripper uses to grasp labware. Recommended values are between 5 and 16. |
| `gripHeightFromLabwareBottom` | Number    | Recommended z-axis height, from the labware bottom to the center of the gripper pads. |

### JSON labware definitions 

| Property {style="width: 20%;"}       | Data type | Definition                                   |
| :-------------- | :-------- | :------------------------------------------- |
| `positiveNumber` | Number    | Minimum: 0.                      |
| `brandData`     | Object    | Information about branded items. Accepts only:<br><ul><li>`brand` (String): Brand/manufacturer's name.</li><li>`brandId` (Array): OEM part numbers or IDs.</li><li>`links` (Array): Manufacturer URLs. Array items are strings.</li></ul> |
| `displayCategory` | String    | Must be one of:<br><ul><li>`tipRack`</li><li>`tubeRack`</li><li>`reservoir`</li><li>`trash`</li><li>`wellPlate`</li><li>`aluminumBlock`</li><li>`adapter`</li><li>`other`</li></ul> |
| `safeString`    | String    | A string safe to use for load names and namespaces. Lowercase letters, numerals, periods, and underscores only. |
| `coordinates`   | Object    | Coordinates that specify a distance or position along the x-, y-, and z-axes. Accepts only:<br><ul><li>`x` (number)</li><li>`y` (number)</li><li>`z` (number)</li></ul> |


---
# Source: modules.md
---

---
title: "Opentrons Flex: Modules"
---

# Modules

Opentrons Flex integrates with several Opentrons hardware modules that add features and capabilities to the robot. Modules can occupy deck slots or are external, frame-mounted components. Flex communicates with and controls most modules via a USB connection.

This chapter summarizes the functions and physical specifications of modules that are compatible with Opentrons Flex. It also covers the caddy attachment system and module calibration.

!!!tip
    - For complete instructions on module installation and use, refer to the quickstart guide that shipped with your unit or find its manual in the [documentation and manuals section](https://opentrons.com/resources/knowledge-hub?c%5B%5D=documentation-manuals) of the Opentrons website.

    - For details on integrating modules into your protocols, see the [Protocol Designer section](protocol-development.md#protocol-designer) of the Protocol Development chapter or the [Hardware Modules section](https://docs.opentrons.com/v2/new_modules.html) of our Python API documentation.


## Supported modules

Opentrons Flex is compatible with with the following Opentrons modules:

- The **Absorbance Plate Reader** is a fully automated spectrophotometer that uses light absorbance to determine sample concentrations. This module is optimized for a variety of applications, including protein quantification, sample normalization, cell viability assays, and monitoring bacterial growth.

- The **Heater-Shaker Module** provides on-deck heating and orbital shaking. The module can be heated to 95 °C, and can shake samples from 200 to 3000 rpm.

- The **HEPA/UV Module** is a positive-pressure clean air and ultraviolet disinfectant accessory for Opentrons Flex. A single 15-minute filtration and UV cycle is sufficient to create an ISO-5 clean bench environment within the Flex enclosure.

- The **Magnetic Block** is a passive device that holds labware close to its high-strength neodymium magnets. The OT-2 Magnetic Module GEN1 and GEN2, which actively move their magnets up and down relative to labware, are not supported on Opentrons Flex.

- The **Temperature Module** is a hot and cold plate module that is able to maintain steady state temperatures between 4 and 95 °C.

- The **Thermocycler Module** provides on-deck, fully automated thermocycling, enabling automation of upstream and downstream workflow steps. Thermocycler GEN2 is fully compatible with the gripper. Thermocycler GEN1 cannot be used with the gripper, and is therefore not supported on Opentrons Flex.

Some modules originally designed for the OT-2 are compatible with Flex, as summarized in the table below. A checkmark :heavy_check_mark: indicates compatibility, and an :heavy_multiplication_x: indicates incompatibility.


| Device type and generation    | OT-2                     | Flex                     |
|:------------------------------|:------------------------:|:------------------------:|
| Absorbance Plate Reader       | :heavy_multiplication_x: | :heavy_check_mark:       |
| Heater-Shaker Module GEN1     | :heavy_check_mark:       | :heavy_check_mark:       |
| HEPA Module                   | :heavy_check_mark:       | :heavy_multiplication_x: |
| HEPA/UV Module                | :heavy_multiplication_x: | :heavy_check_mark:       |
| Magnetic Block GEN1           | :heavy_multiplication_x: | :heavy_check_mark:       |
| Magnetic Module GEN1          | :heavy_check_mark:       | :heavy_multiplication_x: |
| Magnetic Module GEN2          | :heavy_check_mark:       | :heavy_multiplication_x: |
| Temperature Module GEN1       | :heavy_check_mark:       | :heavy_multiplication_x: |
| Temperature Module GEN2       | :heavy_check_mark:       | :heavy_check_mark:       |
| Thermocycler Module GEN1      | :heavy_check_mark:       | :heavy_multiplication_x: |
| Thermocycler Module GEN2      | :heavy_check_mark:       | :heavy_check_mark: 

## Module caddy system

Compatible modules are designed to fit into caddies that occupy space below the deck. This system allows labware on top of modules to remain closer to the deck surface, and it also allows for below-deck cable routing so the deck stays tidy during your protocol runs.

<figure class="side-by-side" markdown>
![Caddy for the Heater-Shaker Module.](images/caddy-heater-shaker.png "Heater-Shaker caddy")
![Caddy for the Temperature Module.](images/caddy-temperature-module.png "Temperature Module caddy")
![Caddy for the Thermocycler Module.](images/caddy-thermocycler.png "Thermocycler caddy")
<figcaption>
Caddies for the Heater-Shaker, Temperature, and Thermocycler Modules.
</figcaption>
</figure>

To fit a module into the deck surface, it must first be placed into the corresponding module caddy. Each type of compatible module has its own caddy design that aligns the module and labware precisely with the surrounding deck. (The exception is the Magnetic Block, which does not require power or USB cable routing and thus sits directly on the deck surface.) Caddies for modules that occupy a single slot can be placed anywhere in column 1 or 3; the Thermocycler can only be placed in slots A1 and B1 simultaneously.

In general, to install a module caddy:

1.  Remove any deck slots from the location where the module will go.

2.  Seat the module into its caddy and tighten its anchors.

3.  Route the module power and USB cables through the side covers, up through the empty deck slot, and attach them to the module.

4.  Seat the module caddy into the slot and screw it into place.

For exact installation instructions, consult the Quickstart Guide or Instruction Manual for the specific module. Cable connections and method of attachment to the caddy vary by module.

!!!warning
    The Heater-Shaker Module and Temperature Module have asymmetrical 4-pin DIN power connectors. When connecting the power cable:

    * Align the connector's flat side with the flat side of the module's power port.
    * Connect the cable to the module first, before plugging it in to a wall outlet.

    ![DIN power connector](images/module-power-connector.png){width="40%"}

    _Do not_ force cable connections, or you may damage the module.

## Module calibration

When you first install a module on Flex, you need to run automated positional calibration. This process is similar to positional calibration for instruments, and ensures that Flex moves to the exact correct locations for optimal protocol performance. During calibration, Flex will move to locations on a module calibration adapter, which looks similar to the calibration squares that are part of removable deck slots.

<figure class="side-by-side" markdown>
![Calibration adapter for the Heater-Shaker Module.](images/calibration-adapter-heater-shaker.png "Heater-Shaker calibration adapter")
![Calibration adapter for the Temperature Module.](images/calibration-adapter-temperature-module.png "Temperature Module calibration adapter")
![Calibration adapter for the Thermocycler Module.](images/calibration-adapter-thermocycler.png "Thermocycler calibration adapter")
<figcaption>
Calibration adapters for the Heater-Shaker, Temperature, and
Thermocycler Modules.
</figcaption>
</figure>

Calibration is required for some modules that use a separate caddy, specifically the Heater-Shaker, Temperature, and Thermocycler Modules.

Other modules do not require calibration and are ready for use upon installation. These include the Absorbance Plate Reader Module (which ships preinstalled in its caddy), the HEPA/UV Module, and the Magnetic Block.

### When to calibrate modules

Flex automatically prompts you to perform calibration when you connect and power on a module that doesn't have any stored calibration data. (You can dismiss this prompt, but you won't be able to run protocols with the module until you calibrate it.)

Once you've completed calibration, Flex stores the calibration data and module serial number for future use. Flex won't prompt you to recalibrate unless you delete the calibration data for that module in the robot settings. You can freely power your module on and off, or even move it to another deck slot, without needing to recalibrate. If you want to recalibrate, you can begin the process at any time from the module card in the Opentrons App. (Recalibration is not available from the touchscreen.)

### How to calibrate modules

Instructions on the touchscreen or in the Opentrons App will guide you through the calibration procedure. In general the steps are:

1.  Gather the required equipment, including the module calibration adapter and pipette calibration probe.

2.  Place the calibration adapter on the module surface and ensure that it is completely level. Some modules may require you to fasten the adapter to the module.

3.  Attach the calibration probe to a pipette.

4.  Flex will automatically move to touch certain points on the calibration adapter and save these calibration values for future use.

Once calibration is complete and you've removed the adapter and probe, the module will be ready for use in protocols.

At any time, you can view and manage your module calibration data in the Opentrons App. Go to **Robot Settings** for your Flex and click on the **Calibration** tab.

## Absorbance Plate Reader

![plate reader hero](images/plate-reader-hero-lid-off.png)

### Plate reader features

The Opentrons Absorbance Plate Reader Module is a deck-mounted, fully automated spectrophotometer. It uses light absorbance to determine sample concentrations. This module is ideal for a broad array of applications, including protein quantification, sample normalization, cell viability assays, and bacterial growth monitoring. The plate reader is designed for indoor laboratory research and other non-in-vitro diagnostic analyses.

!!!note
    The Opentrons Flex Absorbance Plate Reader Module may currently not be offered, used or put on the market in any European Patent Convention States due to a third-party patent application.

#### Measurement capabilities

The plate reader uses 96 separate detection units for rapid sample analysis. The detection units use light in the 400–700 nanometer (nm) range to determine sample concentrations.

#### Gripper compatibility

The Opentrons Flex Gripper is required when using the plate reader. The Gripper is needed to move labware and the plate reader's lid, onto and off the module.

#### Deck placement

The plate reader fits in deck slots A3–D3 only. It comes preinstalled in a caddy, which helps secure the unit to the deck. This module does not require calibration, but you can run Labware Position Check on any installed labware.

#### Software control

The plate reader is fully programmable in Protocol Designer and the Python Protocol API.

### Plate reader specifications

<table>
    <tr>
        <th>Specification</th>
        <th>Description</th>
    </tr>
    <tr>
        <td><strong>Dimensions</strong></td>
        <td>155.3 mm L x 95.5 mm W x 57 mm H</td>
    </tr>
    <tr>
        <td><strong>Weight</strong></td>
        <td>~790 g</td>
    </tr>
    <tr>
        <td><strong>Module power</strong></td>
        <td>
            <ul>
                <li>Input: USB 5 VDC, 3 A</li>
                <li>Consumption: 2.5 W</li>
                <li>Fuse: 1 A (very fast acting)</li>
            </ul>
        </td>
    </tr>
    <tr>
        <td><strong>Detection</strong></td>
        <td>
            <ul>
                <li>Hardware: 96 photodiodes</li>
                <li>Wavelengths: The plate reader emits light in the visible spectrum at 450 nm (blue), 562 nm (green), 600 nm (orange) and 650 nm (red).</li>
            </ul>
        </td>
    </tr>
    <tr>
        <td><strong>Measurement methods</strong></td>
        <td>
            <ul>
                <li>Method: Absorbance</li>
                <li>Techniques: Endpoint and kinetic</li>
                <li>Range: 0–4.0 OD</li>
                <li>Resolution: 0.001 OD</li>
            </ul>
        </td>
    </tr>
    <tr>
        <td><strong>Accuracy</strong></td>
        <td>The maximum deviation between the determined value and the true value.<br><br>At 405 nm:
            <ul>
                <li>≤ 1.5% + 0.010 OD from 0.0–2.0 OD</li>
                <li>≤ 3% + 0.010 OD from 2.0–3.0 OD</li>
            </ul>At or above 450 nm:
            <ul>
                <li>≤ 1% + 0.010 OD from 0.0–2.0 OD</li>
                <li>1.5% + 0.010 OD from 2.0–3.0 OD</li>
            </ul>
        </td>
    </tr>
    <tr>
        <td><strong>Linearity</strong></td>
        <td>The maximum deviation between the true and determined increase of the value.<br><br>At 405 nm:
            <ul>
                <li>≤ 1.5% from 0.0–2.0 OD</li>
                <li>≤ 3% 2.0–3.0 OD</li>
            </ul>At or above 450 nm:
            <ul>
                <li>≤ 1% from 0.0–2.0 OD</li>
                <li>≤ 1.5% from 2.0–3.0 OD</li>
            </ul>
        </td>
    </tr>
    <tr>
        <td><strong>Reproducibility</strong></td>
        <td>The maximum deviation between the determined values when the measurement is repeated directly.<br>
            <ul>
                <li>≤ 0.5% + 0.005 OD from 0.0–2.0 OD</li>
                <li>≤ 1% + 0.010 OD from 2.0–3.0 OD</li>
            </ul>
        </td>
    </tr>
</table>

## Heater-Shaker Module GEN1

![The Heater-Shaker module as seen from the front left. The top of the module has the heating and shaking platform and labware latch. The left side of the module has the power button, USB port, and power port.](images/heater-shaker-module.png "Heater-Shaker Module")

### Heater-Shaker features

#### Heating and shaking

The Heater-Shaker provides on-deck heating and orbital shaking. The
module can be heated to 95 °C, with the following temperature profile:

- Temperature range: 37–95 °C

- Temperature accuracy: ±0.5 °C at 55 °C

- Temperature uniformity: ±0.5 °C at 55 °C

- Ramp rate: 10 °C/min

The module can shake samples from 200 to 3000 rpm, with the following
shaking profile:

- Orbital diameter: 2.0 mm

- Orbital direction: Clockwise

- Speed range: 200–3000 rpm

- Speed accuracy: ±25 rpm

The module has a powered labware latch for securing plates to the module
prior to shaking.

#### Thermal adapters

A compatible thermal adapter is required for adding labware to the Heater-Shaker. Currently available Thermal Adapters include:

<div class="parts-list" markdown>
<figure markdown>
![Adapter with flat plate and prongs on one side to press against the labware latch.](images/heater-shaker-adapter-universal.png "Heater-Shaker Universal Flat Adapter")
<figcaption>Universal Flat Adapter </figcaption>
</figure>

<figure markdown>
![Adapter with indentations to hold 96-well PCR plates.](images/heater-shaker-adapter-pcr.png "Heater-Shaker PCR Adapter")
<figcaption>PCR Adapter</figcaption>
</figure>

<figure markdown>
![Adapter with raised sides for deep well plates.](images/heater-shaker-adapter-deep-well.png "Heater-Shaker Deep Well Adapter")
<figcaption>Deep Well Adapter</figcaption>
</figure>

<figure markdown>
![Adapter with flat bottom and sides to fit 96-well plates with circular wells.](images/heater-shaker-adapter-flat-bottom.png "Heater-Shaker 96 Flat Bottom Adapter")
<figcaption>96 Flat Bottom Adapter</figcaption>
</figure>
</div>

You can purchase adapters directly from Opentrons:

- [Universal Flat Adapter](https://opentrons.com/products/universal-flat-adapter/)
- [PCR Adapter](https://opentrons.com/products/pcr-adapter/)
- [Deep Well Adapter](https://opentrons.com/products/deep-well-adapter/)
- [96 Flat Bottom Adapter](https://opentrons.com/products/96-flat-bottom-adapter/)

#### Software control

The Heater-Shaker is fully programmable in Protocol Designer and the Python Protocol API. The Python API additionally allows for other protocol steps to be performed in parallel while the Heater-Shaker is active. See [Non-blocking commands](https://docs.opentrons.com/v2/modules/heater_shaker.html#non-blocking-commands) in the API documentation for details on adding parallel steps to your protocols.

Outside of protocols, the Opentrons App can display the current status of the Heater-Shaker and can directly control the heater, shaker, and labware latch.

### Heater-Shaker specifications

<table>
  <thead>
    <tr>
      <th>Specification</th>
      <th>Details</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>Dimensions</strong></td>
      <td>152 × 90 × 82 mm (L/W/H)</td>
    </tr>
    <tr>
      <td><strong>Weight</strong></td>
      <td>1.34 kg</td>
    </tr>
    <tr>
      <td><strong>Module power input</strong></td>
      <td>36 VDC, 6.1 A</td>
    </tr>
    <tr>
      <td><strong>Power adapter input</strong></td>
      <td>100–240 VAC, 50/60 Hz</td>
    </tr>
    <tr>
      <td><strong>Mains supply voltage fluctuation</strong></td>
      <td>±10%</td>
    </tr>
    <tr>
      <td><strong>Overvoltage</strong></td>
      <td>Category II</td>
    </tr>
    <tr>
      <td><strong>Power consumption</strong></td>
      <td>
        Idle: 3 W<br />Typical:
        <ul>
          <li>Shaking: 4–11 W</li>
          <li>Heating: 10–30 W</li>
          <li>Heating and shaking: 10–40 W</li>
        </ul>
        Maximum: 125–130 W
      </td>
    </tr>
    <tr>
      <td><strong>Environmental conditions</strong></td>
      <td>Indoor use only</td>
    </tr>
    <tr>
      <td><strong>Ambient temperature</strong></td>
      <td>20–25 °C</td>
    </tr>
    <tr>
      <td><strong>Relative humidity</strong></td>
      <td>Up to 80%, non-condensing</td>
    </tr>
    <tr>
      <td><strong>Altitude</strong></td>
      <td>Up to 2,000 m above sea level</td>
    </tr>
    <tr>
      <td><strong>Pollution degree</strong></td>
      <td>2</td>
    </tr>
  </tbody>
</table>

## HEPA/UV Module

![hepa-uv hero](images/hepa-uv-hero.png)

The top-mounted Opentrons Flex HEPA/UV Module is a clean air and ultraviolet (UV-C) disinfectant accessory for the Flex liquid handling robot. It contains a mesh pre-filter, a HEPA filter, and two UV lights. During operation, the HEPA system creates a positive pressure environment inside the Flex enclosure, which helps protect samples from contamination. When running the UV lights and air filtration for a full, 15-minute cycle, the HEPA/UV module can achieve ISO-5 clean bench standards within the Flex enclosure.

!!!warning
    The HEPA/UV Module is not a biosafety cabinet. Do not use it with pathogens or to filter particles smaller than 0.3 micrometers (μM).

### HEPA/UV Module features

#### Air filtration

The HEPA/UV Module relies on a 2-stage filtration system to purify air pulled into the enclosure. This system includes a reusable pre-filter and a disposable H14 HEPA main filter. The pre-filter traps large particles while the HEPA filter captures up to 99.99% of airborne particulate matter at ≥ 0.3 μm. Vertical air flow from the filter creates a positive pressure environment within the enclosure.

#### UV disinfection

The HEPA/UV Module uses two compact fluorescent bulbs that emit UV-C light at a wavelength of 254 nm. After a 15-minute exposure cycle, the UV light produced is sufficient to reach log-4 (99.99%) inactivation of commonly targeted microorganisms within the enclosure.

#### Safety features

The HEPA/UV Module includes safety features that protect you from UV-C exposure and prevent it from operating in an unsafe manner.

- Panels: The robot's polycarbonate door and side panels block UV spectrum light to below a level that represents an exposure risk.

- Door switch: Flex uses a mechanical switch to tell if the front door is open or closed. The UV lights only work when the front door is closed.

- Attachment sensors: The Flex and HEPA/UV module each have a built-in sensor to detect if the module is attached properly. The sensors deactivate/disable the UV lights if the module is not mounted on the robot, removed while in operation, or misaligned.

### HEPA/UV Module specifications

<table>
    <tr>
        <th>Specification</th>
        <th>Description</th>
    </tr>
    <tr>
        <td><strong>Dimensions</strong></td>
        <td>87 cm L x 64 cm W x 14 cm H</td>
    </tr>
    <tr>
        <td><strong>Weight</strong></td>
        <td>~20 kg (42 lbs)</td>
    </tr>
    <tr>
        <td><strong>Power input</strong></td>
        <td>
            <ul>
                <li>100–240 VAC, 50/60 Hz</li>
                <li>2.2 A at 115 VAC</li>
                <li>1.1 A 230 VAC</li>
            </ul>
        </td>
    </tr>
    <tr>
        <td><strong>Power output</strong></td>
        <td>24 VDC, 8.4 A, 201 W max</td>
    </tr>
    <tr>
        <td><strong>Filter</strong></td>
        <td>
            <ul>
                <li>Metal mesh pre-filter, reusable</li>
                <li>H14 HEPA secondary filter, good for 3 years/6,000 hours, disposable</li>
            </ul>
        </td>
    </tr>
    <tr>
        <td><strong>Ambient fan noise</strong></td>
        <td>≤ 70 dB at 1 meter during operation</td>
    </tr>
    <tr>
        <td><strong>Bulb type</strong></td>
        <td>
            <ul>
                <li>Actinic fluorescent</li>
                <li>2G11 base (4 pin, single-cap)</li>
            </ul>
        </td>
    </tr>
    <tr>
        <td><strong>Bulb life</strong></td>
        <td>
            <ul>
                <li>9,000 hours</li>
                <li>UV end-of-life depreciation: 20%</li>
            </ul>
        </td>
    </tr>
    <tr>
        <td><strong>Mercury (Hg) content</strong></td>
        <td>4.4 mg</td>
</table>

## Magnetic Block GEN1
![The Magnetic Block has an array of 96 high-strength magnets.](images/magnetic-block.png "Magnetic Block")

### Magnetic Block features

The Opentrons Magnetic Block GEN1 is a magnetic 96-well plate holder. Magnetic blocks are used in protocols that rely on magnetism to pull particles out of suspension and retain them in well plates during wash, rinse, or other elution procedures. For example, automated NGS preparation; purifying genomic and mitochondrial DNA, RNA, or proteins; and other extraction procedures are all use cases that can involve magnetic blocks.

#### Magnetic components

The Magnetic Block is unpowered, does not contain any electronic components, and does not move magnetic beads up or down in solution. The wells consist of 96 high-strength neodymium ring magnets fixed to a spring-loaded bed, which helps maintain tolerances between the block and pipettes while running automated protocols.

#### Software control

The Magnetic Block GEN1 is fully programmable in Protocol Designer and the Python Protocol API.

Outside of protocols, however, the touchscreen and the Opentrons App *are not* aware of and *cannot* display the current status of the Magnetic Block GEN1. This is an unpowered module. It does not contain electronic or mechanical components that can communicate with the Flex robot. You "control" the Magnetic Block via protocols that use the Opentrons Flex Gripper to add and remove labware from this module.

### Magnetic Block specifications

| **Specification**       | **Details**                     |
|--------------------------|---------------------------------|
| **Dimensions**           | 136 × 94 × 45 mm (L/W/H)       |
| **Weight**               | 1.13 kg                        |
| **Module power**         | None, module is unpowered      |
| **Magnet grade**         | N52 neodymium                  |
| **Environmental conditions** | Indoor use only           |
| **Ambient temperature**  | 20–25 °C                       |
| **Relative humidity**    | 30–80%, non-condensing         |
| **Altitude**             | Up to 2000 m above sea level   |
| **Pollution degree**     | 2                              |

## Temperature Module GEN2

![The Temperature Module as seen from the top left. The top of the module has the heating and cooling surface and temperature display. The side has the power button, USB port, and power port.](images/temperature-module.png "Temperature Module")

### Temperature Module features

#### Heating and cooling

The Opentrons Temperature Module GEN2 is a hot and cold plate module. It is often used in protocols that require heating, cooling, or temperature changes. The module can reach and maintain temperatures ranging from 4 °C to 95 °C within minutes, depending on the module's configuration and contents.

#### Thermal blocks

To hold labware at temperature, the module uses aluminum thermal blocks. The module comes with 24- well and 96-well thermal blocks. The Temperature Module caddy comes with a deep well block and a flat bottom block designed for use with the Flex Gripper. The blocks hold 1.5 mL and 2.0 mL tubes, 96-well PCR plates, PCR strips, deep well plates, and flat bottom plates.

!!! note
    Note: The module also ships with a flat bottom block for the OT-2. Do not use the OT-2 block with Flex. The flat bottom block for Flex has the words “Opentrons Flex” on its top surface. The one for OT-2 does not.


<div class="parts-list" markdown>

<figure markdown>
![24-well aluminum thermal block for Temperature Module](images/temperature-module-block-24-well.png "24-well thermal block")
<figcaption>24-well thermal block </figcaption>
</figure>

<figure markdown>
![96-well aluminum thermal block for Temperature Module](images/temperature-module-block-96-well.png "96-well thermal block")
<figcaption>96-well thermal block</figcaption>
</figure>

<figure markdown>
![Deep well aluminum thermal block for Temperature Module](images/temperature-module-block-deep-well.png "Deep well thermal block")
<figcaption>Deep well thermal block</figcaption>
</figure>

<figure markdown>
![Flat bottom aluminum thermal block for Temperature Module](images/temperature-module-block-flat.png "Flat bottom thermal block")
<figcaption>Flat bottom thermal block for Flex</figcaption>
</figure>

</div>

#### Software control

The Temperature Module is fully programmable in Protocol Designer and the Python Protocol API.

Outside of protocols, the Opentrons App can display the current status of the Temperature Module and can directly control the temperature of the surface plate.

### Temperature Module specifications

<table>
  <thead>
    <tr>
      <th><strong>Specification</strong></th>
      <th><strong>Details</strong></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>Dimensions</strong></td>
      <td>194 × 90 × 84 mm (L/W/H)</td>
    </tr>
    <tr>
      <td><strong>Weight</strong></td>
      <td>1.5 kg</td>
    </tr>
    <tr>
      <td><strong>Module power</strong></td>
      <td>
        <ul>
          <li>Input: 100–240 VAC, 50/60 Hz, 4.0 A</li>
          <li>Output: 36 VDC, 6.1 A, 219.6 W max</li>
        </ul>
      </td>
    </tr>
    <tr>
      <td><strong>Environmental conditions</strong></td>
      <td>Indoor use only</td>
    </tr>
    <tr>
      <td><strong>Ambient temperature</strong></td>
      <td>&lt;22 °C (recommended for optimal cooling)</td>
    </tr>
    <tr>
      <td><strong>Relative humidity</strong></td>
      <td>Up to 60%, non-condensing</td>
    </tr>
    <tr>
      <td><strong>Altitude</strong></td>
      <td>Up to 2000 m above sea level</td>
    </tr>
    <tr>
      <td><strong>Pollution degree</strong></td>
      <td>2</td>
    </tr>
  </tbody>
</table>

## Thermocycler Module GEN2

![The Thermocycler as seen from the top right. The lid is open to show the thermal block inside.](images/thermocycler.png "Thermocycler")

### Thermocycler features

The Opentrons Thermocycler Module is a fully automated on-deck thermocycler designed for hands-free PCR in a 96-well plate format. It is compatible with the Flex Gripper, other deck-mounted hardware, and is fully supported in the Opentrons App and Python API. When used with a reusable rubber seal or single-use PCR plate lid, the module's heated lid provides a tight seal that helps ensure efficient sample heating and minimizes evaporation, crucial for reliable and repeatable experimental results.

#### Heating and cooling

The Thermocycler's block can heat and cool, and its lid can heat, with the following temperature profile:

- Thermal block temperature range: 4–99 °C

- Thermal block maximum heating ramp rate: 4.25 °C/s from GEN2 ambient to 95 °C

- Thermal block maximum cooling ramp rate: 2.0 °C/s from 95 °C to ambient

- Lid temperature range: 37–110 °C

- Lid temperature accuracy: ±1 °C

The automated lid can be opened or closed as needed during protocol execution.

#### Thermocycler profiles

The Thermocycler can execute *profiles*: automatically cycling through a sequence of block temperatures to perform heat-sensitive reactions.

#### Thermocycler lid seals

The Thermocycler works with two different plate seals to help protect your samples. These are the the [Opentrons Tough PCR Auto-sealing Lid](https://opentrons.com/products/opentrons-flex-tough-auto-sealing-lids-20-count) and reuseable [rubber automation seals](https://opentrons.com/products/gen2-thermocycler-seals).

| Lid Type | Description |
|----|----|
| Opentrons Tough PCR Auto-sealing Lid | These sterile, single-use PCR plate lids help prevent cross-contamination and evaporation during Thermocycler incubation periods. The lids are Gripper-compatible and can be stacked directly on the deck or placed in a special deck riser. |
| Rubber Automation Seal | These are adhesive-backed ethylene propylene diene monomer (EPDM) seals you manually apply to the Thermocycler lid. Rubber seals can be reused up to 20 times; however, unlike the Opentrons Tough Auto-sealing Lid, they are not sterile. The seals must be cleaned and sanitized before each use. |

!!!warning
    Do not use the Opentrons Tough Auto-sealing PCR Lid and a rubber automation seal on the Thermocycler at the same time. This combination prevents the module's lid from closing properly, which can cause temperature control problems and mechanical damage. Always remove the rubber seal before running protocols that use the disposable PCR lid.
    ![PCR lid and rubber seal warning](images/thermocycler-lid-warning.png)

#### Software control

The Thermocycler is fully programmable in Protocol Designer and the
Python Protocol API.

Outside of protocols, the Opentrons App can display the current status
of the Thermocycler and can directly control the block temperature, lid
temperature, and lid position.

### Thermocycler specifications

| Specification                    | Details                                          |
|----------------------------------|--------------------------------------------------|
| **Dimensions (lid open)**        | 244.95 × 172 × 310.1 mm (L/W/H)                  |
| **Dimensions (lid closed)**      | 244.95 × 172 × 170.35 mm (L/W/H)                 |
| **Weight (including rear duct)** | 8.4 kg                                           |
| **Power adapter voltage**        | 100–240 V at 50/60 Hz                            |
| **Power adapter current**        | 8.5–5 A                                          |
| **Overvoltage**                  | Category II                                      |
| **Environmental conditions**     | Indoor use only                                  |
| **Ambient temperature**          | 20–25 °C (ideal); 2–40 °C (acceptable)           |
| **Relative humidity**            | 30–80%, non-condensing                           |
| **Altitude**                     | Up to 2000 m above sea level                     |
| **Ventilation requirements**     | At least 20 cm / 8 in between the unit and a wall|


---
# Source: open-source-software.md
---

---
title: "Opentrons Flex: Open-Source Software"
---

# Open-Source Software

Opentrons believes that open-source software and hardware make science
better. That's why we make our code available on GitHub and welcome
contributions from the open-source community.

This appendix covers various ways to use Opentrons open-source resources
and describes the structure of our repositories.

## Opentrons on GitHub

The Opentrons GitHub organization can be found at <https://github.com/Opentrons>. All of our publicly
hosted code resides there, including the Flex robot software, the
Opentrons App, and our Python and HTTP APIs.

Our GitHub site has several useful resources for Flex users, and you can
participate in our community even if you're not a coder.

!!! note
    As you browse our GitHub repositories, you will encounter references to `ot3`, which is a model identifier for Opentrons Flex. If you're having trouble finding something when searching for "Flex", try searching for "ot3" or "OT-3" instead.

## Opentrons monorepo

Most of our software is in the [Opentrons/opentrons](https://github.com/Opentrons/opentrons) *monorepo*: a single repository that
contains multiple software projects, each in its own directory. The
`README.md` file in each directory describes the project and gives advice
on working with the code. The default branch in the monorepo is called
`edge`.

The following (non-exhaustive) list of directories, subdirectories, and
files can help you navigate the monorepo and find code relevant to using
Flex.

| Path {width="25%"} | Description |
|------|-------------|
| [`/api/`](https://github.com/Opentrons/opentrons/tree/edge/api) | Source for the Python Protocol API, written in Python and distributed as the `opentrons` PyPI package. |
| [`/api/docs/`](https://github.com/Opentrons/opentrons/tree/edge/api/docs) | Documentation for the Python Protocol API, written in ReStructuredText. |
| [`/api/release-notes.md`](https://github.com/Opentrons/opentrons/blob/edge/api/release-notes.md) | Release notes for the robot system software (as a whole, including changes outside of the `/api/` directory). |
| [`/app-shell-odd/`](https://github.com/Opentrons/opentrons/tree/edge/app-shell-odd) | Electron application wrapper for the touchscreen software — "odd" stands for *on-device display*. |
| [`/app-shell/`](https://github.com/Opentrons/opentrons/tree/edge/app-shell) | Electron application wrapper for the Opentrons App. |
| [`/app-shell/build/`<br>`release-notes.md`](https://github.com/Opentrons/opentrons/blob/edge/app-shell/build/release-notes.md) | Release notes for the Opentrons App (as a whole, including changes outside of the `/app-shell/` directory). |
| [`/app/`](https://github.com/Opentrons/opentrons/tree/edge/app) | Source for the Opentrons App. Use `make` commands in this directory to run the app from source. |
| [`/labware-library/`](https://github.com/Opentrons/opentrons/tree/edge/labware-library) | Source for the Labware Library website. |
| [`/protocol-designer/`](https://github.com/Opentrons/opentrons/tree/edge/protocol-designer) | Source for Protocol Designer, our no-code web application for creating JSON protocol files. |
| [`/robot-server/`](https://github.com/Opentrons/opentrons/tree/edge/robot-server) | The web service that runs the Opentrons HTTP API. The Opentrons App and touchscreen use HTTP API calls to control the robot. You can also write your own software that makes HTTP API calls or use software like `curl` or Postman to make individual calls to a robot. |
| [`/shared-data/`](https://github.com/Opentrons/opentrons/tree/edge/shared-data) | Special directory for data that needs to be shared between projects. |
| [`/shared-data/labware/`](https://github.com/Opentrons/opentrons/tree/edge/shared-data/labware) | Schema and labware definitions for Opentrons-verified labware. The Python Protocol API and Labware Library both use the definition files stored here. |
| [`/shared-data/python/`](https://github.com/Opentrons/opentrons/tree/edge/shared-data/python) | Source for the `opentrons-shared-data` Python package, which is a dependency of the main `opentrons` package. |

## Other repositories

Opentrons also maintains software outside of the monorepo. A few key
repositories include:

| Repository {width="25%"} | Description |
|---|---|
| [`oe-core`](https://github.com/Opentrons/oe-core) | The heart of Opentrons' [openembedded](https://www.openembedded.org/wiki/Main_Page) system definitions. |
| [`opentrons-emulation`](https://github.com/Opentrons/opentrons-emulation) | Emulation of Opentrons robots and modules at either the hardware or firmware level. Uses [Docker](https://www.docker.com/), configuration files, and a simple command-line interface. |
| [`opentrons-modules`](https://github.com/Opentrons/opentrons-modules) | Firmware for all Opentrons modules. |
| [`ot3-firmware`](https://github.com/Opentrons/ot3-firmware) | Firmware for Opentrons Flex and all of its peripheral systems. |

---
# Source: preface.md
---

---
title: "Opentrons Flex: Preface"
---

# Preface

Welcome to the instruction manual for the Opentrons Flex liquid handling robot. This manual guides you through just about everything you need to know to set up and use Flex, focusing on topics that are most relevant to everyday users of Flex in a lab environment.

## Structure of this manual

Opentrons Flex is a complex system, so there are many different paths to learning everything it can do. Feel free to jump straight to the chapter that addresses whatever topic you're curious about! For example, if you already have a Flex set up in your lab, you can skip past the Installation and Relocation chapter.

If you prefer a guided approach, this manual is structured so you can follow it from beginning to end.

- **Learn about Flex.** The distinguishing features of Flex are listed in [Chapter 1: Introduction](introduction.md). The introduction also includes important safety and regulatory information.

- **Get started with Flex.** If you need to set up your Flex, follow the detailed instructions in [Chapter 2: Installation and Relocation](installation-relocation.md). Then familiarize yourself with the components of Flex in [Chapter 3: System Description](system-description.md).

- **Set up your deck.** Configuring the deck enables different scientific applications on Flex.  [Chapter 4: Modules](modules.md) describes Opentrons peripherals that you can install into or on top of the deck to perform specific scientific tasks. [Chapter 5: Labware](labware.md) explains how to work with equipment for holding liquids.

- **Run a protocol.** The core use of Flex is running standardized scientific procedures, known as protocols. [Chapter 6: Protocol Development](protocol-development.md) offers several ways to get ready-made protocols or design them yourself. To run your protocol, follow the instructions in [Chapter 7: Software and Operation](software-operation.md), which also has instructions for performing other tasks and customizing your robot's settings.

- **Keep Flex running.** Follow the advice in [Chapter 8: Maintenance and Service](maintenance-service.md) to keep your Flex clean and running optimally. Or sign up for one of the Opentrons services listed there and let us take care of Flex for you.

- **Learn even more.** Still need something else? Consult the appendices.

    - [Appendix A: Glossary](glossary.md) defines Flex-related terms.

    - [Appendix B: Additional Documentation](additional-documentation.md) points you to even more resources for Opentrons products and writing code to control Flex.
    
    - [Appendix C: Open-Source Software](open-source-software.md) explains how Opentrons software is hosted on GitHub as a resource for both developers and non-developers.
    
    - [Appendix D: Support and Contact Information](support-contact-information.md) lists how to get in touch with Opentrons if you need assistance beyond what our documentation provides.

## Notes and warnings

Throughout this manual, you'll find specially formatted note and warning
blocks. Notes provide helpful information that may not be obvious in the
ordinary course of using Flex. Pay special attention to warnings---they
are only used in situations where you run the risk of personal injury,
damage to equipment, loss or spoilage of samples or reagents, data loss,
or other harm.

Notes and warnings look like this:

!!! note
    **Sample Note:** This is something you ought to know, but it doesn't pose any danger.

!!! warning
    **Sample Warning:** This is something you need to know because there is risk associated with it.


---
# Source: protocol-development.md
---

---
title: "Opentrons Flex: Protocol Development"
---

# Protocol Development

The Opentrons Flex system can run a wide variety of automated protocols, for tasks such as PCR, NGS, ELISA, and many more. You can run fully built and verified protocols, edit community protocols to suit your needs, or design protocols from scratch—with or without writing code.

This chapter provides an overview of each of these protocol development methods, as well as giving guidance on how to adapt protocols written for the Opentrons OT-2 to run on Opentrons Flex.

## Pre-made protocols

### Protocol Library

The Opentrons Protocol Library hosts protocols authored either by Opentrons itself or by members of the Opentrons community. To find a protocol that fits your target application, use the search field at the top of the [Protocol Library homepage](https://library.opentrons.com).

You can also browse protocols by categories, like DNA/RNA, cell biology, cell and tissue culture, proteins, commercial assay kits, or molecular biology. There's even a category for protocols that create art by pipetting! Take some time to check out the protocols in our library. Understanding what's available—and making some cool pixel art—is a great way to learn about the features and capabilities of your robot before moving on to using real samples and reagents.

#### Searching for protocols

The Protocol Library search returns results as you type. You can select a result from the search list or click **View All Results** to go to the full results page, which shows more details about each protocol and lets you filter them based on several criteria.

Each protocol card will show:

| **Category**                | **Description**                                                                                                                                         |
|--------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Protocol name**        | The name of the protocol.                                                                                                                               |
| **Verification**         | Badges indicate if the protocol is verified by Opentrons, a third-party manufacturer, or members of the community.                                      |
| **Time estimate**        | Approximately how long the protocol takes to run.                                                                                                       |
| **Description**          | A short summary of what the protocol does.                                                                                                              |
| **Robot model**          | Which Opentrons robots the protocol is compatible with.                                                                                                 |
| **Protocol editability** | JSON protocols are editable in Protocol Designer, with no coding required. Python protocols are editable in any text editor, using the Python Protocol API. |
| **Modules**              | Any hardware modules that are required.                                                                                                                 |

In addition to these categories, in the sidebar you can filter results
by:

- **Pipettes:** Which pipettes the protocol uses (you can usually change a protocol's pipettes, but it may affect the run time and the number of tips consumed).

- **Categories:** Target applications, like DNA/RNA, cell biology, proteins, etc.

- **Protocol version:** Show or hide older versions of protocols.

#### Protocol details

Click on a protocol to go to its detail page, which provides even more information. In addition to what is shown in search, here you can see:

- **Supporting data:** Additional data, explanations, or links to outside sources provided by the protocol author.

- **What you'll need:** A complete list of all equipment needed for the protocol, including the robot, modules, labware, pipettes, and third-party kits.

- **Protocol steps:** A list of steps written by the protocol author, as well as a visual deck map and list of liquids specified in the protocol file.

The details page also provides basic instructions for downloading and running the protocol. For more information on importing a protocol to the Opentrons App and setting up a run, see the [Transferring Protocols to Flex section][transferring-protocols-to-flex] in the Software and Operation chapter.

### Custom Protocol Development service

Opentrons provides a [Remote Custom Protocol Development service](https://opentrons.com/instrument-services) for applications not already included in the Protocol Library. Our comprehensive authoring and validation service has a turnaround time of two weeks. As part of the service, Opentrons field applications scientists will:

- Develop the Python protocol.

- Validate the code.

- Install the protocol remotely.

- Create deck and reagent setup instructions.

- Optimize your protocol as much as needed within one week of initial delivery.

By default, Opentrons adds all custom protocols to the Protocol Library so the community can benefit from them. However, if your application requires privacy, you can opt out of inclusion in the Protocol Library.

!!! note
    The Custom Protocol Development service only writes Python protocols that control Opentrons hardware. It does not cover controlling the robot with code in other languages, nor does it cover controlling third-party hardware.

#### Protocol request guidelines

Describing your protocol in detail enables Opentrons field applications scientists to accurately code the automation that you need. Consider your protocol's requirements, including:

- Hardware (pipettes, gripper, modules, fixtures).

- Labware (Opentrons verified, other standard, or custom).

Also consider special cases that apply to your protocol, like:

- Liquids that are volatile, viscous, or otherwise behave differently than water.

- Conservation of expensive reagents.

- Sterility and cross-contamination.

- Advanced pipetting techniques like air-gapping, high or low flow rate, or pipetting at specific locations within wells.

To explain the movements the robot will make in executing the protocol, start with your initial deck state. Where should modules, labware, and trash containers be located? Which liquids will be in which labware, and in what quantities? Use the coordinate systems printed on the Opentrons Flex deck and on standard labware to describe these locations.

Next, give step-by-step instructions on how Opentrons Flex should handle liquids, specifying quantities in microliters (µL) and giving exact source and destination locations (rows, columns, or individual wells of labware).

In general, following the style of the methods section of an academic paper will help the Opentrons team understand your instructions. And always err on the side of providing extra information—it may be exactly the detail we need to write code for your protocol.

#### Custom protocol pricing

Custom Protocol Development is a service available to all owners of Opentrons Flex systems. Opentrons provides remote and onsite protocol development services customized to your specific workflow. Price and development time are based on the complexity of your protocol and the related code. See the [Instrument Services section](https://opentrons.com/instrument-services) of the Opentrons website to contact us for more information about our Custom Protocol Development offerings.

## Protocol Designer

Protocol Designer is a web-based, no-code tool for developing protocols that run on Opentrons robots, including Opentrons Flex. You can use Protocol Designer to create protocols that:

- Aspirate, dispense, transfer, and mix liquids.

- Move labware around the deck with the gripper.

- Operate Opentrons Flex modules.

- Pause to let you verify progress or access samples.

All work on your protocol takes place within your web browser. When
you're done creating or editing your protocol, you need to export it to
a JSON file. Then upload that file to a robot and run it, as you would
with any protocol.

### Protocol Designer requirements

Currently, Protocol Designer is only supported for use in Google Chrome
and requires an internet connection. Uploading and running JSON
protocols on Opentrons Flex requires version 7.0.0 or later of the
Opentrons App.

You can't create or modify Python protocol files with Protocol Designer.

### Designing a protocol

Protocols are all about informing the robot what hardware it will use to
take specific actions. This process is broken down into three tabs in
Protocol Designer:

**Icon Tab**

The **File tab** is where you manage protocol files and specify hardware
for use in your protocol.

The **Liquids tab** lets you define samples, reagents, and any other
liquids that your robot will handle.

The **Design tab** is where you specify the initial state of the deck,
add steps that the robot will perform, and view the projected outcomes
of those steps.

To create a protocol from scratch, you'll start on the File tab, work
with the Liquids and Design tabs, and then return to the File tab to
export your work. The remainder of this section goes through the
protocol creation process in detail.

#### Part 1: Create a protocol

When you launch Protocol Designer, you'll begin on the **File** tab. In
the left sidebar, click **Create New** to open the Create New Protocol
dialog. Click on the image of Opentrons Flex and then click **Next**.

Choosing to create a protocol for Opentrons Flex in Protocol Designer.

Enter a name for your protocol, which is how it will appear in the
Opentrons App and on the touchscreen. You'll also see your protocol name
in the Protocol Designer header while you're working on it. Optionally
add a description and author information for your protocol.

Next, Protocol Designer guides you through choosing the hardware used in
your protocol:

1.  Pipettes and what type of tip racks you'll use with them. Every
    protocol requires at least one pipette.

2.  Staging area slots in column 3 (optional).

3.  Additional hardware used in your protocol, such as modules, the
    gripper, or the waste chute. Only are shown.

!!! note
    You can't currently use multiple Heater-Shaker Modules or Magnetic Blocks in a JSON protocol. If your application requires them, you'll need to use a Python protocol. See the below.

At any time, you can return to the File tab to rename your protocol, add
an author name or description, or change your hardware configuration.

#### Part 2: Define liquids

Move on to the **Liquids** tab to set up samples and reagents. This tab
is only for *defining* types of liquids. You'll indicate the starting
positions and amounts of liquids in Part 3, on the Design tab.

Click **New Liquid** and then enter the name of your liquid and an
optional description. You can also choose whether to *serialize* the
liquid, so each well containing that liquid will be numbered on the deck
map and in action steps. For example, if your protocol has blood
samples, serialization can help you keep them separate in your workflow,
while still labeling them all as "blood" and color-coding them the same.

Each type of liquid appears in a different color on the deck map in
Protocol Designer, in the Opentrons App, and on the touchscreen. You can
use the default color, pick another preset color, or enter an RGB hex
code to set a custom color.

#### Part 3: Lay out the deck

Go to the Design tab to do the final setup step, which is placing
labware and liquids on the deck. The main view on this tab is the deck
map, which shows everything on the deck down to individual wells ---
even on 384-well plates.

The deck map starts with the tip racks and modules you chose for your
protocol in their default locations. Hover over any open slot and click
**Add Labware or Adapter** to add more tip racks, other types of
labware, or adapters. Drag and drop labware to an open slot to move it
there, or to an occupied slot to swap the two pieces of labware.

!!! note
    You can'tmove modules or adapters around the deck map by drag and drop. This is to make it easier to move *labware* onto or off of a module.

- To change a module's position, return to the **File** tab and click
  **Edit** next to the module name.

- To change an adapter's position, add a new adapter. Then move the
  labware from the old adapter to the new adapter. Finally, delete the
  old adapter.

Hover over any labware and click **Add Liquids** to specify which wells
contain which liquid. Clicking on a single well or dragging across a
range of wells will reveal a form at the top of the screen. Choose one
of the liquids you defined and the volume *each* well should start with,
in μL. For example, if you select the first column on a 96-well plate
and specify 100 μL, that will be 800 μL of liquid total (100 μL × 8
wells).

#### Part 4: Add steps

At last, it's time to tell your robot how to move liquid around the
deck. Click **Add Step** and choose the type of step.

- Pipetting steps

  - **Transfer:** Move liquid from one well or group of wells to
    another. Specify the source, where liquid will be aspirated from, on
    the left. Specify the destination, where liquid will be dispensed,
    on the right. Click either gear icon to change behaviors such as
    flow rate, tip height, knocking droplets off (touch tip), air
    gapping, blowout, and more. In the Sterility & Motion section,
    choose the correct tip-use strategy for your application.

  - **Mix:** Repeatedly aspirate and dispense liquid within the same
    well. Choose how much liquid to mix with, the number of mixing
    repetitions, and which wells will be mixed. Like with transfer
    steps, click either gear to change mixing behavior. You can also
    choose a tip-use strategy for mixing. These options are more limited
    than for transfers, since all liquid returns to its starting
    location when mixing.

- Gripper steps

  - **Move Labware:** Control the Flex Gripper or move labware around
    the deck manually. Choose which labware you want to move and its new
    location. Check the **Use Gripper** box to have the gripper move the
    labware automatically, or leave it unchecked to have the protocol
    pause so you can move the labware manually. You need to use the
    gripper to dispose labware by moving it into the waste chute. You
    need to move labware manually to move it off the deck (without
    disposing it).

- Module steps

  - **Heater-Shaker:** Control the temperature, shake speed, and labware
    latch of the Heater-Shaker Module. You can set an optional timer
    that will pause the protocol for a set period of time *after* the
    other actions are completed (heating to high temperatures or waiting
    for the module to passively cool to a temperature can take a long
    time).

  - **Temperature:** Set a target temperature or deactivate the
    Temperature Module.

  - **Thermocycler:** This action has two mutually exclusive sets of
    options.

    - Change Thermocycler state: Set a block temperature, set a lid
      temperature, or move the lid.

    - Program a Thermocycler profile: Define a *profile*, a timed
      heating and cooling routine that can be automatically repeated.
      Each step of the profile holds the block at a certain temperature
      for a certain time. Profiles do not change the temperature of the
      lid.

- **Pause:** Prevent the protocol from continuing until one of three
  criteria is met. Pauses can require user intervention (pressing a
  button on the touchscreen or in the app), wait for a fixed time, or
  wait until a module reaches a target temperature. Timed pauses are
  useful for incubation or letting the Magnetic Block work.

#### Part 5: Edit steps

Once you've created a step, preview its effects by hovering over it in
the Protocol Timeline. Affected tips and wells will be highlighted, as
will the entire labware containing those wells.

Show or hide the details of a step by clicking the disclosure triangle
to the right of its name. For liquid handling steps, this will show
every discrete aspirate and dispense pair comprising the step. For
module steps, this will show the features of the module that the step
controls.

Click on the name of a step in the Protocol Timeline to edit it.
Shift-click to select a range of steps and enter batch editing mode. If
you select only transfer or mix steps, you can change their behavior as
a batch. Reorder steps by dragging and dropping them up or down in the
Protocol Timeline.

When editing any step, click **Notes** to change the step name or add a
description of what the step does. Custom step names replace their
default action descriptions (like "Transfer" and "Temperature") in the
Protocol Timeline, making it easier to navigate around your protocol.

#### Part 6: Export your protocol

When your protocol is complete, click **Final Deck State** to preview
how the deck should appear at the end of your protocol. In this view (or
when viewing a particular step), you can click on labware and examine
the expected quantity of liquid in each well.

To save your work, return to the File tab and click **Export** to
download your protocol as a JSON file. The file will have the name you
chose in the Protocol Name field and will have a .json extension. You
can find exported protocols in the default download location of your web
browser.

To run your protocol, import it into the Opentrons App. (See the for
details on installing and using the Opentrons App.) Then either run it
from the app or send it to your Flex to run from the touchscreen.

### Modifying existing protocols

Click **Import** in the File tab to load an existing protocol. Choose
any JSON protocol file from the standard system file picker. Once
loaded, you can edit any aspect of the protocol, including its name,
description, hardware configuration, and steps.

!!! warning
    Importing a protocol will replace any other protocol that you've been working on in Protocol Designer. Be sure to export your work before importing another file, or open Protocol Designer in a second browser tab to work on multiple files at once.

## Python Protocol API

Writing protocol scripts in Python gives you the most fine-grained
control of Opentrons Flex. Version 2 of the Python Protocol API is a
single Python package that exposes a wide range of liquid handling
features on Opentrons robots. For an idea of the breadth of the API,
check out the [full online documentation](https://docs.opentrons.com/v2/), which includes topic-based articles as well as a [comprehensive reference](https://docs.opentrons.com/v2/new_protocol_api.html) of all
methods and functions contained in the package. If you've never written
an Opentrons protocol before and want to build one from scratch, follow
the [Tutorial](https://docs.opentrons.com/v2/tutorial.html).

### Writing and running scripts

Python protocols generally follow the same basic structure:

1.  Importing the `opentrons` package.

2.  Declaring the `requirements` and `metadata` in their respective dictionaries.

3.  Defining a `run()` function that contains all of the instructions to the robot, including:

    - [Pipettes](https://docs.opentrons.com/v2/new_pipette.html) the protocol will use.

    - Locations of [modules](https://docs.opentrons.com/v2/new_modules.html), [labware](https://docs.opentrons.com/v2/new_labware.html), and [deck fixtures](https://docs.opentrons.com/v2/deck_slots.html#deck-configuration).

    - [Liquid](https://docs.opentrons.com/v2/new_labware.html#labeling-liquids-in-wells) types and locations (optional).

    - Commands the system will physically execute (e.g., [simple](https://docs.opentrons.com/v2/new_atomic_commands.html) or [complex](https://docs.opentrons.com/v2/new_complex_commands.html) liquid
      handling commands, [module](https://docs.opentrons.com/v2/new_modules.html) commands, or [movement](https://docs.opentrons.com/v2/robot_position.html) commands).

```python
from opentrons import protocol_api
requirements = {"robotType": "Flex", "apiLevel": "2.15"}

def run(protocol):

    # labware
    plate = protocol.load_labware(
        "corning_96_wellplate_360ul_flat", location="D1"
    )
    tip_rack = protocol.load_labware(
        "opentrons_flex_96_tiprack_200ul", location="D2"
    )

    # pipettes
    left_pipette = protocol.load_instrument(
        "flex_1channel_1000", mount="left", tip_racks=[tip_rack]
    )

    # commands
    left_pipette.pick_up_tip()
    left_pipette.aspirate(100, plate["A1"])
    left_pipette.dispense(100, plate["B2"])
    left_pipette.drop_tip()

```

If you're running a protocol via the Opentrons App or the touchscreen, you don't need to call the `run()` function, because the robot software does it for you.

However, one of the advanced features of the Python API is to control a robot outside of the usual flow for setting up and running a protocol. Opentrons Flex runs a Jupyter Notebook server, which can execute discrete blocks of code (called *cells*), rather than a complete protocol file. When organizing your code into cells, you can define a `run()` function (and then call it) or run commands without one. It's also possible to execute complete protocols in a Jupyter terminal session or when connected to Flex via SSH. For more information, see the [Advanced Operation section][advanced-operation] of the Software and Operation chapter.

### Python-exclusive features

Certain features are only available in Python protocols, either because they are part of the API or because of the inherent flexibility of Python code.

#### Partial tip pickup

The Python API supports the most partial tip pickup configurations. Currently, JSON protocols only support column pickup with the 96-channel pipette. The `InstrumentContext.configure_nozzle_layout()` method supports these additional layouts:

- Row pickup with the 96-channel pipette.

- Partial column pickup with 8-channel pipettes.

- Single tip pickup with all multi-channel pipettes.

Certain configurations allow changing which nozzles are used. For example, you can pick up a column of tips with either the left or right edge of the 96-channel pipette.

#### Runtime parameters

Starting in API version 2.18, you can define user-customizable variables in your Python protocols. This gives you greater flexibility and puts extra control in the hands of the technician running the protocol --- without forcing them to switch between lots of protocol files or write code themselves.

Runtime parameters can customize Boolean, numerical, and string values in your protocol. And starting in API version 2.20, you can require a CSV file of data to be parsed and used in the protocol. See the [API documentation on runtime parameters](https://docs.opentrons.com/v2/runtime_parameters.html) for information on writing them into protocols, and see the Runtime Parameters section of the Software and Operation chapter for information on changing parameter values during run setup.

#### Non-blocking commands

Some module commands that take a long time to complete (such as heating from ambient temperature to a high temperature) can be run in a *non-blocking* manner. This lets your protocol save time by continuing on to other pipetting tasks instead of waiting for the command to complete. Non-blocking commands are currently supported on the [Heater-Shaker Module](https://docs.opentrons.com/v2/modules/heater_shaker.html#non-blocking-commands).

#### Multiple modules of the same type

The Python API only restricts module placement based on physical limitations. Protocol Designer can only place one of each type of module on the deck, except the Temperature Module. [`ProtocolContext.load_module()`](https://docs.opentrons.com/v2/new_protocol_api.html#opentrons.protocol_api.ProtocolContext.load_module) allows placing any powered module in any column 1 or 3 slot (except the Thermocycler Module, which only fits in slots A1 and B1). And it allows placing Magnetic Blocks in any working area slot.

#### Python packages

Not only does the Python API support some features not included in Protocol Designer, but every Python protocol *is a Python script*, which means that it can perform any computation that relies on the Python standard libraries or the suite of libraries included in the Flex system software.

You can even install additional Python packages on Flex. [Connect to your Flex via SSH][command-line-operation-over-ssh] and install the package with `pip`. To avoid analysis errors in the Opentrons App, install the packages on your computer as well. In the Opentrons App settings, go to **Advanced** and click **Add override path** in the Override Path to Python section. Choose the copy of `python` on your system that has access to the packages.

## OT-2 protocols

There are hundreds of OT-2 protocols in the Protocol Library, and you may have created your own OT-2 protocols for your lab. Opentrons Flex can perform all the basic actions that the OT-2 can, but OT-2 protocols aren't directly compatible with Flex. However, with a little effort, you can adapt an OT-2 protocol so it will run on Flex. This lets you have parity across different Opentrons robots in your lab, or you can extend older protocols to take advantage of new features only offered on Flex.

### OT-2 Python protocols

Using the Python Protocol API, you only have to change a few aspects of an OT-2 protocol for it to run on Flex.

#### Metadata and requirements

The API requires you to declare that a protocol is designed to run on Flex. Use the `robotType` key in the new `requirements` dictionary. You should also specify an `apiLevel` of 2.15 or higher. You can specify `apiLevel` either in the `metadata` dictionary or the `requirements`
dictionary.

```python
from opentrons import protocol_api
requirements = {'robotType': 'Flex', 'apiLevel': '2.15'}
```

#### Pipettes and tip racks

Flex uses different types of pipettes and tip racks than OT-2, which have their own load names in the API. Choose pipettes of the same capacity or larger (or whatever you've outfitted your Flex with).

For example, you could convert an OT-2 protocol that uses a P300 Single-Channel GEN2 pipette and 300 µL tips to a Flex protocol that uses a Flex 1-Channel 1000 µL pipette and 1000 µL tips:

```python
# Original OT-2 code
def run(protocol: protocol_api.ProtocolContext):
    tips = protocol.load_labware("opentrons_96_tiprack_300ul", 1)
    left_pipette = protocol.load_instrument(
        "p300_single_gen2", "left", tip_racks=[tips]
    )
```

```python
# Modified Flex code
def run(protocol: protocol_api.ProtocolContext):
    tips = protocol.load_labware("opentrons_flex_96_tiprack_1000ul", "D1")
    left_pipette = protocol.load_instrument(
        "flex_1channel_1000", "left", tip_racks[tips]
    )
```


The only necessary changes are the new arguments of `load_labware()` and `load_instrument()`. Keep in mind that if you use smaller capacity tips than the original protocol, you may need to make further adjustments to avoid running out of tips, and the protocol may take longer to execute.

#### Deck slots

The API accepts OT-2 and Flex deck slot names interchangeably. It's good practice to use the coordinate deck slot format in Flex protocols (as in the example in the previous subsection), but it's not required. The correspondence between deck slot numbers is as follows:

<table>
  <tr>
    <th>Flex</th>
    <td>A1</td>
    <td>A2</td>
    <td>A3</td>
    <td>B1</td>
    <td>B2</td>
    <td>B3</td>
    <td>C1</td>
    <td>C2</td>
    <td>C3</td>
    <td>D1</td>
    <td>D2</td>
    <td>D3</td>
  </tr>
  <tr>
    <th>OT-2</th>
    <td>10</td>
    <td>11</td>
    <td>Trash</td>
    <td>7</td>
    <td>8</td>
    <td>9</td>
    <td>4</td>
    <td>5</td>
    <td>6</td>
    <td>1</td>
    <td>2</td>
    <td>3</td>
  </tr>
</table>

A protocol that calls `#!python protocol.load_labware("opentrons_flex_96_tiprack_200ul", "1")` would require you to place that tip rack in slot D1 on Flex.

#### Modules

Update module load names for the Temperature Module and Thermocycler Module to ones that are compatible with Flex, if necessary. Flex supports:

- `temperature module gen2`

- `thermocycler module gen2` or `thermocyclerModuleV2`

The Heater-Shaker Module only has one generation, which is compatible
with Flex and OT-2.

For protocols that load `magnetic module`, `magdeck`, or `magnetic module
gen2`, see [Magnetic Module Protocols][magnetic-module-protocols] below.

### OT-2 JSON protocols

Currently, Protocol Designer can't convert an OT-2 protocol to a Flex protocol. You have to choose which robot the protocol will run on when you create it.

Since Flex protocols support nearly all the features of OT-2 protocols, you can create a new protocol that performs all the same steps, but is designed to run on Flex. The simplest way to do this is:

1.  Launch Protocol Designer and import your OT-2 protocol.

2.  Open a second browser window and launch Protocol Designer there.

3.  Create a new Flex protocol in the second browser window.

4.  Set up the Flex hardware as similarly as possible as the OT-2 hardware. For example, choose pipettes of the same capacity or larger, and choose modules of the same type.

5.  Replicate the liquid setup and steps from the OT-2 protocol.

6.  Export your Flex protocol. Import it into the Opentrons App and check the run preview to see that it performs the same steps as your OT-2 protocol.

You can make bigger changes if your Flex configuration differs significantly from your OT-2 configuration, but you may need to re-verify your protocol.

### Magnetic Module protocols

Note that there is no direct analogue of the Magnetic Module on Flex. You'll have to use the Magnetic Block and Flex Gripper instead. This will require reworking some of your protocol steps, and you should verify that your new protocol design achieves similar results.


---
# Source: software-operation.md
---

---
title: "Opentrons Flex: Software and Operation"
---

# Software and Operation

There are multiple ways to control Opentrons Flex, depending on the needs of your lab. You can perform most functions either from the touchscreen or from a computer running the Opentrons App. This chapter will focus primarily on touchscreen operation, and will only cover features of the Opentrons App that are not possible on the touchscreen. It will also outline advanced control features, such as running Python code using the Jupyter Notebook server or from the command line of Flex.

One major difference between touchscreen and app operation is the software's relationship to the robot. The touchscreen is integrated, and therefore only controls the Flex robot that it's physically a part of. In contrast, the Opentrons App can control any number of Opentrons robots connected to the computer that's running the app. Using both pieces of software is required to set up Flex and run your first protocol, but it's up to you to decide the balance of how you will control Flex in your daily workflow.

## Touchscreen operation

You can use the touchscreen to control Flex whenever the robot is on. If your robot is on and the touchscreen is off, tap it once to wake the screen.

### Robot dashboard

<figure class="screenshot" markdown>
![The robot dashboard, showing main navigation and recently run protocols.  ](images/touchscreen-dashboard.png "Robot dashboard")
</figure>

The dashboard is the main screen for the robot, accessible by tapping the robot's name in the top left corner of the touchscreen.

The dashboard provides quick access to recently run protocols. It displays protocols as large cards in a horizontal carousel. Green cards show protocols that are ready to run. Orange cards show protocols that require hardware setup or have a deck configuration conflict. The dashboard can display up to eight previously run protocols.

From the dashboard you can also perform actions that apply to the robot as a whole, rather than a particular protocol. Access these actions by tapping the three-dot (⋮) menu:

- **Home gantry:** Move the gantry to its home position at the back right of the working area.

- **Restart robot:** Perform a soft restart of the robot.

- **Deck configuration:** Manage deck fixture locations.

- **Lights on/off:** Toggle the LED lights that illuminate the working area.

The top navigation on the dashboard provides access to the other main screens: All Protocols, Quick Transfer, Instruments, and Settings. Next we'll look at how to manage protocols on the All Protocols screen

### Protocol management

The All Protocols screen is an interactive list of all protocols that you've stored on Opentrons Flex. (Sending a protocol to Flex requires the Opentrons App. See the [Transferring Protocols to Flex section][transferring-protocols-to-flex] below for details on that process.)

There are two sections of the All Protocols screen:

- Pinned protocols: Large cards in a horizontal carousel at the top of the screen.

- Other protocols: A vertical list at the bottom of the screen.

<figure class="screenshot" markdown>
![The All Protocols screen, showing pinned protocols at the top and other protocols at the bottom.](images/touchscreen-all-protocols.png "All Protocols screen")
</figure>

Regardless of which section a protocol is in, its card or list entry includes information about when it was last run and when it was added to this robot.

!!! note
    Flex can store a maximum of 20 unique protocols. It automatically deletes older protocols to maintain this limit. Use the Opentrons App if you need to manage a larger number of protocols.

#### Pin a protocol

Long press on a protocol and tap **Pin protocol** to move it to the pinned protocols section. Conversely, long press a pinned protocol and tap **Unpin protocol** to remove it from the section.

<figure class="screenshot" markdown>
![The protocol long-press menu, with three options: Run protocol, Pin protocol, and Delete protocol.](images/touchscreen-protocol-menu.png "Protocol menu")
</figure>

You can pin up to eight protocols. When you hit the maximum, you'll need to unpin a protocol before pinning another one.

#### Sort protocols

Tap any of the three headers — Protocol Name, Last Run, or Date Added — to sort the All Protocols section.

Tap once to sort protocols in ascending order (A to Z for names, oldest to newest for dates). Tap again to reverse the sort order. The current sort criterion is highlighted in blue and the current sort order is indicated by an upward or downward arrow.

#### Delete a protocol

Long press on a protocol and tap **Delete protocol** to delete it directly from the All Protocols screen. Flex will prompt you for confirmation that you want to delete the protocol file and all of its run history.

<figure class="screenshot" markdown>
![Modal confirming whether to delete a protocol.](images/touchscreen-delete-protocol.png "Deleting a protocol")
</figure>

!!! warning
    Run history is *not recoverable* after you delete a protocol on Flex. The protocol file itself is also not recoverable, although you may be able to resend the protocol to Flex if you've kept a copy of it on a computer.

### Protocol details

Tap on any protocol to view its detail screen. This screen displays all of the types of information included in the protocol file, as well as common protocol actions. An indicator at the top left of the screen shows whether the protocol is ready to run, or whether you need to perform additional setup.

#### Summary tab

<figure class="screenshot" markdown>
![Summary of an RNA extraction protocol showing author, description, date, and action buttons.](images/touchscreen-protocol-summary.png "Protocol summary")
</figure>

The Summary tab shows:

- **Protocol name:** For protocols with very long names, tap to toggle between the full and truncated name.

- **Author:** Who created the protocol.

- **Description:** For protocols with long descriptions, scroll to read the full text.

- **Date added:** Timestamp when Flex received the protocol file.

#### Parameters tab

<figure class="screenshot" markdown>
![List of parameters for an RNA extraction protocol, such as number of samples, source sample volume, wash volume, and elution volume.](images/touchscreen-protocol-parameters.png "Protocol parameters")
</figure>

The Parameters tab lists all of the runtime parameters that you can configure from the touchscreen while setting up the protocol. The Default Value column shows the value that the protocol will use if you don't change it. The Range column shows the maximum and minimum, list of choices, or number of choices depending on the parameter type.

!!! note
    Runtime parameters are only available in Python protocols that define their names, descriptions, and possible values. See [Runtime Parameters](https://docs.opentrons.com/v2/runtime_parameters.html) in the Python API documentation for information on defining parameters and using their values. JSON protocols do not currently support this feature.

#### Hardware tab

<figure class="screenshot" markdown>
![List of hardware for an RNA extraction protocol, including pipette, gripper, and modules.](images/touchscreen-protocol-hardware.png "Protocol hardware")
</figure>

The Hardware tab is a list of all instruments, modules, and fixtures used in the protocol. The Location column tells you where the hardware needs to be attached to Flex. For instruments, location can be the left pipette mount, right pipette mount, both mounts (for the 96-channel pipette), or the extension mount (for the gripper). For modules and fixtures, the location is the deck slot or slots that the item occupies.

#### Labware tab

<figure class="screenshot" markdown>
![List of labware for an RNA extraction protocol, such as deep well plates, reservoirs, and tip racks.](images/touchscreen-protocol-labware.png "Protocol labware")
</figure>

The Labware tab is a list of all labware used in the protocol. It shows the names and quantities of labware. It does not show their locations, since labware can be moved, added, or removed from the deck during the course of a protocol. Use the Deck tab to see initial positions of labware.

Opentrons-verified labware is indicated with a blue checkmark.

#### Liquids tab

<figure class="screenshot" markdown>
![List of liquids for an RNA extraction protocol, including various buffers.](images/touchscreen-protocol-liquids.png "Protocol liquids")
</figure>

The Liquids tab lists all liquids to be loaded into labware at the start of the protocol. It shows the color code of the liquid (as assigned by the protocol author), the liquid name, and the total volume of liquid used across all wells. Use the Deck tab to see well-by-well initial positions of liquids.

#### Deck tab

<figure class="screenshot" markdown>
![Deck map for an RNA extraction protocol, showing locations of labware on the Flex deck.](images/touchscreen-protocol-deck.png "Protocol deck map")
</figure>

The Deck tab shows a visual map of the deck at the beginning of the protocol.

For an interactive view that provides more information about the contents of each deck slot, tap **Start setup**, then tap **Labware**, and then tap **Map View**. There you can tap on any labware to see its type and custom label (if set by the protocol).

#### Action buttons

On any of the protocol detail tabs, three action buttons are available:

- **Start setup** (top right)

- **Pin protocol** (bottom left)

- **Delete protocol** (bottom right)

Next we'll look at the steps for setting up and performing a protocol run.

### Run setup

When you start setup for a protocol, you'll see the "Prepare to run" screen, which summarizes all of the requirements for the protocol.

<figure class="screenshot" markdown>
![Prepare to run screen for a nucleic acid purification protocol, showing instrument setup as complete (green); module and deck setup as incomplete (orange); and Labware Position Check, labware setup, and liquid setup as not started (grey).](images/touchscreen-prepare-to-run.png "Prepare to run")
<figcaption>All sections of the "Prepare to run" screen. On the touchscreen, scroll the list to see all sections.</figcaption>
</figure>

If hardware is not connected or calibrated, you will see a warning icon (exclamation point) and the row will be highlighted in orange. If all requirements are met, you will see a checkmark and the row will be highlighted in green.

Tap any row with a right arrow to show more information for that category. (The one exception is tapping Labware Position Check, which begins that process. See the Labware Position Check section below for more details.)

| Category   | Description |
|------------|------------|
| Instruments    | See if all instruments are attached to the correct mounts and calibrated.<br />Tap <b>Attach</b> or <b>Calibrate</b> to set up any that aren't. |
| Parameters     | See the names, descriptions, and default values of runtime parameters for the protocol.<br />Tap a parameter to edit its value. See the Runtime Parameters section below for more details. |
| Hardware       | See the locations and connection statuses of hardware on the deck.<br><ul><li>Tap :fontawesome-solid-circle-info: <b>Setup Instructions</b> to get detailed instructions.</li><li>Tap <b>Map View</b> to switch to a visual layout of hardware positions.</li></ul> |
| Labware        | See the locations of labware. Each labware lists its initial deck location, and icons indicate labware that are on top of modules.<br />Tap <b>Map View</b> to switch to a visual layout of labware positions. |
| Liquids        | See the types and total volumes of liquids.<br />Tap any liquid name to expand a list of well-by-well volumes. In turn, tap an individual volume row to show a visual layout of its location within labware. |

On any category screen, return to the "Prepare to run" screen by tapping the back arrow in the top left.

### Runtime parameters

Runtime parameters customize protocols during setup, letting you adjust pipette types, mount positions, aspirate/dispense volumes, labware types, and more—all without writing a new protocol.

<figure class="screenshot" markdown>
![Parameter modification screen. This example includes a CSV file and numeric parameters.](images/touchscreen-run-setup-parameters.png "Runtime parameters")
</figure>

Tap a configurable parameter to modify it. Different types of touchscreen controls are used for different parameter types.

- **Boolean:** Tap the parameter to toggle its value between On and Off.

- **String and numeric choices:** Choose from a menu of possible values.

- **Numeric range:** Use the onscreen keypad to enter a value within the acceptable range.

- **CSV:** Choose from a file picker.

#### Using CSV data

Flex looks for CSV files in the root directory of an attached USB drive or files that were used in a previous run of the same protocol. You can connect a USB drive to any open USB port on Flex, but we recommend using the port below the touchscreen. As shown here, this protocol has no CSV files saved on this robot, but there are several on an attached USB drive. Tap the desired CSV file to use its data into your protocol.

<figure class="screenshot" markdown>
![CSV file picker, showing no files on the robot and three files on an attached USB drive.](images/touchscreen-run-setup-csv.png "CSV file picker")
</figure>

When working with CSV files, keep in mind that:

- The touchscreen truncates file names that are longer than 52 characters. You can still upload files with names that exceed the limit.

- The USB drive must use a file system that's readable by the robot. FAT32, NTFS, and ext4 file systems are supported. The HFS+ and APFS file systems are not.

- You must leave the USB drive attached until you start the run, or Flex won't be able to access the CSV data that you chose.

#### Confirming runtime parameters

Parameter and CSV file selections are still editable until you tap **Confirm values**. Modifications become read-only after that. To make further adjustments, you'll have to cancel the protocol run and start over.

### Labware offsets and position checking

#### Labware offsets
Labware offsets are fine-tuned positional coordinates that help your robot align its pipette relative to a specific piece of labware. The release of robot software version 8.4 introduced significant improvements to the labware offset and position checking system.

| Feature | Description |
|----|----|
| Protocol independence | Offsets are positional adjustments associated with a piece of labware, rather than with a specific protocol, and saved on the robot. This allows for greater flexibility and reusability of offset data in any protocol. |
| Default offsets | Default offsets are manually created via Labware Position Check and then automatically applied to each instance of that labware, regardless of deck slot or protocol. This "measure once, set everywhere" feature means you don't have to check offsets for duplicate labware, which helps reduce protocol setup time and effort. |
| Applied offsets | Applied offsets override defaults for a specific piece of labware in a specific deck slot. You can use an applied offset with different protocols, but the labware and deck slot must be the same as the original applied offset. |
| Hardcoded offsets | A hardcoded offset is an offset type typically created by advanced users via the Opentrons Python API. Because these offsets are defined in code (`set_offset`), you cannot change them from the touchscreen or Opentrons App. You’ll need to modify the Python protocol file to change a hardcoded offset. See [Setting Labware Offsets](https://docs.opentrons.com/v2/new_advanced_running.html?highlight=offset#setting-labware-offsets). |

#### Offsets at-a-glance

This illustration shows how the different types of offsets appear as you're configuring a protocol on the Flex touchscreen.

![](images/labware-offsets.svg)

#### Labware Position Check

Labware Position Check lets you align a pipette relative to a piece of labware (e.g. a well plate), which helps ensure accurate and reproducible pipetting results.

You must ensure that each piece of labware used in your protocol has a default or applied offset associated with it. As shown in the touchscreen example below, you cannot run a protocol (the blue run button is inactive) if it uses labware that is missing offset data.

<figure class="screenshot" markdown>
![Touchscreen showing missing labware offset](images/missing-offsets.png)
</figure>

Tap **Labware Offsets** to see which labware is missing an offset and to start Labware Position Check. Refer to the touchscreen or the Opentrons App when running Labware Position Check. It will provide instructions and animations to guide you through this process.

#### Jog controls

During Labware Position Check, you’ll use the jog controls to align the pipette with the selected labware.

<figure class="screenshot" markdown>
![Jog controls, with three options for jump size on the left, toggle between axes in the middle, and arrow buttons on the right.](images/touchscreen-lpc-jog-controls.png "Labware Position Check jog controls")
<figcaption>Jog controls used in Labware Position Check.</figcaption>
</figure>

To use the jog controls:

1. Select a jog control option to set the pipette's axis of movement.
2. Select a jump size to set how far the pipette moves (in mm). You can move the pipette in increments of 0.1, 1, or 10 mm.  Use larger jump sizes to move the pipette quickly, but beware of crashing the pipette into labware.
3. Tap an arrow to move the pipette for your selected direction and distance.
4. Tap **Close** when, in your best judgement, the pipette is optimally aligned with the selected labware.
5. Continue to follow prompts and instructions on the touchscreen to complete the Labware Position Check process.

!!! note
    Labware Position Check corrects for minor, millimeter-scale pipette and labware alignment variations. If you find yourself using it to compensate for large, multi-centimeter offsets, this may suggest an alignment problem related to labware manufacturing defects or incorrect labware definitions. Contact Opentrons Support if you encounter persistent, significant instrument or labware misalignments.

### Run progress

Once everything is set up, begin your run by tapping the play button :material-play-circle: on the "Prepare to run" screen. Flex will begin the protocol and you'll see the Running screen.

The Running screen gives you quick access to stop and play/pause controls, in case you need to intervene in your protocol. On the default view, these controls are large and only the current step of the protocol is shown.

<figure class="screenshot" markdown>
![Running screen with large stop and pause buttons, and a description of a single aspirate step.](images/touchscreen-running-one-step.png "touchscreen-running-one-step.png")
</figure>

Swipe from right to left to see an alternative view with smaller controls and more protocol steps. The current step will always be at the top of the list.

<figure class="screenshot" markdown>
![Running screen with small stop and pause buttons in the top right, and a list of several protocol steps.](images/touchscreen-running-multi-step.png "touchscreen-running-multi-step.png")
</figure>

Starting in robot software version 8.0.0, if something unexpected happens during the protocol run, Flex will pause and give you the option to enter error recovery mode. In earlier versions, Flex cancels the run when an error occurs.

### Error recovery

Flex error recovery allows you to continue a protocol run even when
problems arise.

![Error recovery screen showing a pipette overpressure error, with options to cancel the run or launch recovery mode.](images/touchscreen-error-recovery.png "Error recovery")

Tap **Launch recovery mode** to see options for the particular type of error that has occurred. Instead of just canceling the protocol and forcing a restart, this feature gives you a chance to correct problems like replacing a damaged tip or filling an empty well. Even if you have to cancel a protocol run, error recovery will let you preserve liquids in the pipette and control where tips are dropped. After all, an occasional mistake or problem shouldn't end a procedure with the loss of expensive reagents or valuable samples.

Flex provides a protocol recovery path for the following error conditions.

<table>
  <thead>
    <tr>
      <th>Error type</th>
      <th style="width: 30%;">Description</th>
      <th>Recovery options</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>No liquid detected</td>
      <td>Occurs when a pipette encounters an empty well and expects a liquid to be present.</td>
      <td>
        <ul>
          <li>Manually fill the empty well and retry with the same tips.</li>
          <li>Manually fill the empty well and retry with new tips.</li>
          <li>Manually fill the empty well and skip to the next step.</li>
          <li>Ignore the error and skip to the next step.</li>
          <li>Cancel protocol run.</li>
        </ul>
      </td>
    </tr>
    <tr>
      <td>Pipette overpressure</td>
      <td>Occurs when pressure inside the pipette exceeds the normal range while aspirating or dispensing liquid. Caused by clogged, bent, or sealed tips.</td>
      <td>For aspiration:<br>
        <ul>
            <li>Retry with new tips.</li>
            <li>Cancel protocol run.</li>
        </ul>
        For dispense:
        <ul>
            <li>Skip to the next step with the same tips.</li>
            <li>Skip to the next step with new tips.</li>
            <li>Cancel protocol run.</li>
        </ul>
      </td>
    </tr>
    <tr>
      <td>General errors</td>
      <td>A catch-all category for other errors.</td>
      <td>
        <ul>
          <li>Retry step.</li>
          <li>Skip to next step.</li>
          <li>Cancel protocol run.</li>
        </ul>
      </td>
    </tr> </tbody>
</table>

!!! note
    The tip presence sensor is disabled for [partial tip pickup](system-description.md#partial-tip-pickup) of 1, 2, or 3 tips. In these configurations, Flex cannot detect tip pickup errors and will not present error recovery options if the pipette fails to pick up the tips. The run will continue unless and until another error occurs.

You can view the status of a finished protocol and review any resolved errors on the run completion screen.

### Run completion

At the end of your protocol, a large "Run completed" or "Run failed" message will take over the touchscreen. These color-coded messages match the LED status bar at the top of the robot and are visible at a distance.

<figure class="side-by-side" markdown>
![Green run completed screen.](images/touchscreen-run-completed.png "Run completed")
![Red run failed screen.](images/touchscreen-run-failed.png "Run failed")
</figure>

Tap anywhere on either of these screens to go to the run summary screen, which shows information about the protocol run time and next steps. The summary screen always gives you the options to **Return to dashboard** or have the protocol **Run again**. If the run failed, you can also **View error details** and begin the troubleshooting process.

<figure class="screenshot side-by-side" markdown>
![Summary of a completed run with options to return to dashboard (left) or run again (right).](images/touchscreen-run-summary-failed.png "touchscreen-run-summary-failed.png")
![Summary of a failed run with options to return to dashboard (left), run again (center), or view error details (right).](images/touchscreen-run-summary-completed.png "touchscreen-run-summary-completed.png")
</figure>

### Quick transfer

Quick transfer is a touchscreen-only feature that lets you create, save, and run simple procedures that move liquid from a source to a destination, all without creating a protocol or writing code. Available starting in robot software version 8.0.0, this feature is ideal for preparing labware you need to use in other, more complex procedures. For example, you can use quick transfers to:

- Provision well plates with a reagent, buffer, or other liquid.

- Consolidate liquid from many wells to one well.

- Distribute liquid from a single well to multiple wells.

- Move culture to growth media or to prepare it for long-term storage.

There are two sections of the quick transfer screen:

- **Pinned transfers**: Large cards on a horizontal carousel. You can pin 8 cards, maximum.

- **Saved transfers**: A vertical list at the bottom of the screen. Flex can save a maximum of 20 quick transfers. You have to delete older quick transfers to maintain this limit.

<figure class="screenshot" markdown>
![Quick transfer screen with two pinned quick transfers at the top and a longer list of quick transfers at the bottom.](images/quick-transfer-list.png "Quick transfers")
</figure>

The remainder of this section goes through quick transfer features in detail.

#### Creating a quick transfer

From the Quick Transfer tab on the touchscreen, tap **+ Quick transfer.** This starts a guided setup. Follow the instructions on the screen. You can run, save, pin, or delete the transfer when finished.

#### Deck slots and hardware requirements

Quick transfers require a Flex pipette, a tip rack in slot B2, source labware in slot C2, and destination labware in slot D2. For tip disposal, quick transfer relies on the robot's [deck configuration][deck-configuration] to determine where the trash bin or waste chute is on the deck. It shows the trash bin in slot A3 if no trash container is configured. You cannot use the gripper, modules, and custom labware in a quick transfer.

<figure class="screenshot" markdown>
![Quick transfer deck setup with trash bin in A3, tip rack in B2, source labware in C2, and destination labware in D2.](images/quick-transfer-deck.png "Quick transfer deck setup")
</figure>

If everything is set up correctly, you'll move on to selecting pipettes and tips.

#### Pipettes and tips

Creating a quick transfer involves selecting a pipette and appropriate tips. Quick transfer can use any 1-, 8-, or 96-channel pipette that's attached to the robot. When selecting a pipette tip, try to match the tip to a pipette of the same capacity or larger. For best performance, use the smallest tips that can hold the amount of liquid you need to aspirate.

#### Labware

Quick transfer works with most of the labware in the [Opentrons Labware Library](https://labware.opentrons.com/). It omits labware from the source and destination menus when those items are incompatible with the selected pipette. For example, only the 1-channel pipette can aspirate or dispense from tube racks. If you select a multi-channel pipette, quick transfer won't let you choose a tube rack as a source or destination.

#### Well selection

Well selection depends upon the pipette and labware you're using. When using a 1-or 8-channel pipette and a 96-well plate, you select individual wells by tapping or tapping and dragging on the touchscreen. Or, when using multi-channel pipettes and high-density well plates, quick transfer provides button controls that let you select columns and well groups instead of individual wells.

For example, these controls let you select wells and columns with an 8-channel pipette and a 384-well plate.

<figure class="screenshot" markdown>
![384 well selection screen with 8 wells selected, starting with A1.](images/quick-transfer-well-selection-8-channel.png "8-channel quick transfer")
</figure>

And these controls let you select wells and columns with a 96-channel pipette and 384-well plate.

<figure class="screenshot" markdown>
![384 well selection screen with 96 wells selected, starting with A1.](images/quick-transfer-well-selection-96-channel.png "96-channel quick transfer")
</figure>

Quick transfer checks your pipette, source, and destination choices to prevent incompatible combinations. If you make a mistake while selecting wells, or want to start over, tap **Reset** to clear your selections.

After making instrument and well selections, you'll set the transfer volume and give your new quick transfer a name.

#### Transfer volumes and name

You'll set the amount of liquid to transfer (in μL) after specifying the source and destination wells. You'll also have a chance to name the transfer after setting the transfer volume. A good, concise name helps you find a quick transfer in a list of saved or pinned transfers and indicates what it does.

#### Advanced settings

These are available after you name a quick transfer and before you save it. If some settings are familiar to you that's because they're the same as those offered in Protocol Designer. Advanced settings are optional; select any that you need or just save or run the transfer.

| Setting {style="width: 25%;"} | Description |
|----------|-------------|
| Aspirate and dispense flow rates | Set how quickly the pipette will aspirate or dispense, in μL/s.|
| Pipette path           | Choose how the pipette moves between wells. Options include:<br><ul><li>single transfer (1 well to 1 well)</li><li>multi-aspirate (many wells to 1 well)</li><li>multi-dispense (1 well to many wells)</li></ul> |
| Tip position           | Change where in the well the pipette aspirates or dispenses. By default, the robot positions the tip 1 mm from the bottom center of a well. |
| Pre-wet tip            | Pre-wet the pipette tip by aspirating and dispensing ⅔ of the tip's maximum volume. |
| Mix                    | Aspirate and dispense repeatedly from a single location. Used to mix the contents of a well together. |
| Delay                  | Adds a timed delay (in seconds) before an aspirate or dispense action. |
| Touch tip              | Move the pipette so the tip touches the wall of a well. Used to help knock off any droplets that might cling to the pipette's tip. Not supported on all labware. |
| Air gap                | When used during aspiration, draw in extra air after the liquid. When used during dispense, draw in extra air before moving to the trash container to dispose of the tip. Used to prevent liquid from leaking out of the pipette tip. |
| Blowout                | Blow an extra amount of air through the tip to clear it. The pipette can blow out into the trash bin, source well, or destination well. |
| Change tip             | Replace the tip at the start of the transfer, before every aspirate, or per source well. |

#### Managing transfers

Click **Create Transfer** when you're satisfied with your transfer settings. After creating a quick transfer, you can run, save, or delete it.

- Flex saves a maximum of 20 transfers in a vertical list under the Quick Transfer tab.

- Long press a saved transfer to run it, pin it, or delete it. Flex pins a maximum of 8 quick transfers.

- Long press a pinned transfer to run it, un-pin it (returns it to the saved list), or delete it.

<figure class="screenshot" markdown>
![Menu with options to run, pin, or delete a quick transfer.](images/quick-transfer-menu.png "Quick transfer menu")
</figure>

### Instrument management

The Instruments screen is an interactive list of all instruments that you've connected to your Flex. The list is organized by mount: left pipette mount, right pipette mount, and extension mount.

<figure class="screenshot" markdown>
![Instruments screen showing a Flex 8-Channel 50 µL pipette on the left mount. The right mount and extension mount are empty.](images/touchscreen-instruments.png "Instruments list")
</figure>

For an empty mount, tap anywhere on the row to begin the process of attaching an instrument.

For an occupied mount, the row lists its current contents. Tap anywhere on the row to get more details about the instrument, detach it, or recalibrate it.

<figure class="screenshot" markdown>
![Details for a Flex 8-Channel 50 µL, including calibration, firmware, and serial number.](images/touchscreen-instrument-detail.png "Instrument details")
</figure>

- **Last Calibrated:** The date and time of the instrument's most recent calibration.

- **Firmware Version:** The version of the firmware running on the instrument. Flex automatically updates instrument firmware whenever the instrument is attached, depending on the robot system version.

- **Serial Number:** A unique identifier for the instrument. If you are having problems with an instrument, Opentrons Support will want to know the serial number.

#### Attach an instrument

Choose an empty mount and then choose the type of instrument to install. Then connect and secure the instrument using its captive mounting screws. For more details, follow the instructions on the touchscreen or see the [Instrument Installation and Calibration section][instrument-installation-and-calibration] of the Installation and Relocation chapter.

Exact installation steps depend on the instrument you choose and the current setup of your robot. For example, if you have an 8-channel pipette already attached and you attempt to install the 96-channel pipette on the other mount, the touchscreen will give you instructions for detaching the 8-channel so the 96-channel can occupy both mounts.

#### Detach an instrument

Choose an attached instrument that you want to detach. Then loosen the instrument's captive mounting screws and remove it from the gantry. For more details, follow the instructions on the touchscreen. Exact removal steps depend on the instrument you choose and the current setup of your robot.

#### Recalibrate an instrument

Choose an attached instrument that you want to recalibrate. Then connect the instrument's calibration probe or pin and begin the automated calibration process. For more details, follow the instructions on the touchscreen or see the [Instrument Installation and Calibration section][instrument-installation-and-calibration] of the Installation and Relocation chapter.

!!! note
    The new calibration data will overwrite any previous calibration data for that instrument.

## Opentrons App

### App installation

Download the Opentrons App at <https://opentrons.com/ot-app/>. The app requires Windows 10, macOS 10.10, or Ubuntu 12.04 or later. The app may run on other Linux distributions, but Opentrons does not officially support them.

#### Windows

The Windows version of the Opentrons App is packaged as an installer. To use it:

- Open the .exe file you downloaded from opentrons.com.

- Follow the instructions in the installer. You can install the app for a single user or all users of the computer.

The app opens automatically once installed. Grant the app security or firewall permissions, if prompted, to make sure it can launch and communicate with Flex over your network.

#### macOS

The macOS version of the Opentrons App is packaged as a disk image. To use it:

1.  Open the .dmg file you downloaded from opentrons.com. A window for the disk image will open in Finder.

2.  Drag the Opentrons icon onto the Applications icon in the window.

3.  Double-click on the Applications icon.

4.  Double-click on the Opentrons icon in the Applications folder.

Grant the app security or firewall permissions, if prompted, to make sure it can launch and communicate with Flex over your network.

#### Ubuntu

The Ubuntu version of the Opentrons App is packaged as an AppImage. To use it:

1.  Move the .AppImage file you downloaded from opentrons.com to your Desktop or Applications folder.

2.  Right-click the .AppImage file and choose **Properties**.

3.  Click the **Permissions** tab. Then check **Allow executing file as a program**. Close the Properties window.

4.  Double-click the .AppImage file.

!!! note
    Do not use third-party AppImage launchers with the Opentrons App. They may interfere with app updates. Opentrons does not support using third-party launchers to control Opentrons robots.

### Transferring protocols to Flex

Every protocol will begin as a file on your computer, regardless of what method of [Protocol Development](protocol-development.md) you use. You need to import the protocol into the Opentrons App and then transfer it to your Flex. When transferring a protocol, you can choose to begin run setup immediately or later.

#### Import a protocol

When you first launch the Opentrons App, you will see the Protocols screen. (Click **Protocols** in the left sidebar to access it at any other time.) Click **Import** in the top right corner to reveal the Import a Protocol pane. Then click **Choose File** and find your protocol in the system file picker, or drag and drop your protocol file into the well.

The Opentrons App will analyze your protocol as soon as you import it. *Protocol analysis* is the process of taking the JSON object or Python code contained in the protocol file and turning it into a series of commands that the robot can execute in order. If there are any errors in your protocol file, or if you're missing custom labware definitions, a warning banner will appear on the protocol's card. Correct the errors and re-import the protocol. If there are no errors, your protocol is ready to transfer to Flex.

<figure class="screenshot" markdown>
![Expanded three-dot menu for a protocol, showing these options: Start setup, Reanalyze, Send to Opentrons Flex, Show in folder, and Delete](images/app-protocol-menu.png "Screenshot")
<figcaption>Actions available in the three-dot menu (⋮) for imported protocols.</figcaption>
</figure>

!!! note
    In-app protocol analysis is only a preliminary check of the validity of your protocol. Protocol analysis will run again on the robot once you transfer the protocol to it. It's possible for analysis to fail in the app and succeed on the robot, or vice versa. Analysis mismatches may occur when your app and robot software versions are out of sync, or if you have customized the Python environment on your Flex.

#### Run immediately

Click the three-dot menu (⋮) on your protocol and choose **Start setup**. Choose a connected and available Flex from the list to transfer the protocol and begin run setup immediately. The run setup screen will appear both in the app and on the touchscreen, and you can continue from either place.

If you stay in the app, expand the sections under the Setup tab and follow the instructions in each one: Robot Calibration, Module Setup (if your protocol uses modules), Labware Position Check (recommended), and Labware Setup. Then click :material-play-circle: **Start run** to to begin the protocol.

If you move to the touchscreen, follow the steps in the [Run Setup section][run-setup] above.

#### Run later

Click the three-dot menu (⋮) on your protocol and choose **Send to Opentrons Flex**. Choose a connected and available Flex from the list to transfer the protocol. A message indicating a successful transfer will pop up both in the app and on the touchscreen. To set up your protocol, you need to move to the touchscreen and follow the steps in the [Run Setup section][run-setup] above.

### Module status and controls

Use the Opentrons App to view the status of modules connected to your Flex and control them outside of protocols. Click **Devices** and then click on your Flex to view its robot details page. Under Instruments and Modules, there is a card for each attached module. The card shows the type of module, what USB port it is connected to, and its current status.

<figure markdown>
![Card showing the status of a Heater-Shaker module, including a banner showing that it is currently hot.](images/app-module-status.png "Heater-Shaker status card")
<figcaption>Module card for the Heater-Shaker Module.</figcaption>
</figure>

!!! note
    The Magnetic Block does not have a card in Instruments and Modules, since it is unpowered and does not connect to Flex via USB.

Click the three-dot menu (⋮) on the module card to choose from available commands. You can always choose **About module** to see the firmware version and serial number of the module. (This information is very useful when contacting Opentrons Support!) The other commands depend on the type of the module and its current status:

| Module type    | Commands |
| -------------- | -------- |
| **Heater-Shaker** | <ul><li>Set module temperature / Deactivate heater</li><li>Open labware latch / Close labware latch</li><li>Test shake / Deactivate shaker</li></ul> |
| **Temperature**   | <ul><li>Set module temperature / Deactivate module</li></ul>                            |
| **Thermocycler**  | <ul><li>Set lid temperature / Deactivate lid</li><li>Open lid / Close lid</li><li>Set block temperature / Deactivate block</li></ul> |

### Recent protocol runs

The robot details page lists up to 20 recent protocol runs. This provides additional information compared to the touchscreen, which only shows the most recent run for each unique protocol.

Each entry in the recent protocol runs list includes the protocol name, its timestamp, whether the run was canceled or completed, and the duration of the run. Click the disclosure triangle next to any run to show its associated labware offset data. Click the three-dot menu (⋮) for related actions:

- **View protocol run record:** Show the protocol run screen as it appeared when the protocol ended (succeeded, failed, or was canceled), including all performed steps.

- **Rerun protocol now:** The same as choosing **Start setup** on the corresponding protocol.

- **Download run log:** Save to your computer a JSON file containing information about the protocol run, including all performed steps.

- **Delete protocol run record:** Delete all information about this protocol run from Flex, including labware offset data. When you choose this option, it's as though the protocol run never happened.

!!! note
    If you need to maintain a comprehensive record of all runs performed on your Flex, you must use the **Download run log** feature to save this information to your computer.

Flex *will not* retain information about more than 20 runs on the robot. Proceeding to the Run Setup screen generates an entry in the list and counts towards the maximum of 20 runs, even if you never begin the protocol.

## Command line operation over SSH

You can work with your Flex through a Secure Shell (SSH) terminal connection. Terminal access lets you [run protocols directly from the command line](https://docs.opentrons.com/v2/new_advanced_running.html#command-line) or perform advanced tasks, such as customizing the Python environment on the robot. Protocols that reference external files on disk (apart from custom labware definition files) must be run from the command line.

!!!note
    - SSH keys are required before you can connect to Flex and issue commands from a terminal.
    - If you're unable to use a Wi-Fi network for SSH, see [Hardwired SSH Connections][hardwired-ssh-connections] below.

### Creating SSH keys

Follow these steps to create SSH keys on your Mac, Windows, or Linux computer:

1. Open a terminal window and type this command:

    ```
    ssh-keygen -f robot_key -t ecdsa
    ```

1. Create a passphrase when prompted. This process generates a file, `robot_key.pub`. A passphrase is not required, but you should create one.

1. Copy the `robot_key.pub` file to the root of a USB-A flash drive. You will use this USB drive (and the saved key) for SSH authentication to the robot.

    !!!note
        The flash drive must have a single partition formatted with a file system readable by the embedded Linux system on Flex. FAT32, NTFS, and ext4 file systems are supported. The macOS HFS+ and APFS file systems are not. macOS can read and write to FAT-formatted drives.

1. Eject the USB drive.

### Making an SSH connection

To make an SSH connection:

1. Insert the USB drive that holds the SSH key created earlier into a USB port on your Flex.

1. On your computer, open a terminal window and type the commands shown below. Replace `ROBOT_IP` with the IP address of your Flex.

    ```
    curl \
    --location --request POST \
    'http://ROBOT_IP:31950/server/ssh_keys/from_local'
    ```
    The command is successful when you see a response message that indicates a new key was added.

1. After adding the key, type the command shown below. Replace `ROBOT_IP` with the IP address of your Flex.

    ```
    ssh -i robot_key root@ROBOT_IP
    ```

1. Type the passphrase you set when creating the SSH key.

When an SSH connection is successful, the terminal command prompt changes to `root@` followed by the serial number of your robot (e.g., `root@FLXA1020231007001:~#`). You can now interact with the robot via the terminal window.

### Hardwired SSH connections

A hardwired connection uses an Ethernet cable to connect and transmit data directly between your computer and Flex. This is a secure alternative for SSH access in situations where network policies prevent you from making a wireless connection to the robot.

!!!note
    The hardwired SSH procedure requires assigning a static IP address to the robot. You may want to ask for help from your IT support team before proceeding.

#### Physical connection

Connect a computer to the robot using an Ethernet cable. If your computer has a built-in RJ-45 Ethernet port, plug one end into the computer and connect the other end to the Ethernet port on the robot. If you're using a computer without an Ethernet port, use an adapter with an Ethernet port to make this connection.

When disconnected from a network, your Flex will assign itself an IP address and subnet mask. You'll need this information to set a static address on your computer within the same IP address range and subnet as your Flex.

#### Finding the robot's IP address

You can get the IP address range and subnet mask from the robot by connecting it to your computer and checking the Opentrons App:

1. If the robot is connected by Ethernet cable to a switch or wall jack, disconnect it. Then establish a physical Ethernet connection to your computer, as described above.

1. Launch the Opentrons App.

1. Click the **Devices** tab and find your robot.

    !!!note
        If your robot appears as inactive or inaccessible in the app, wait a few moments. Flex will configure itself and eventually become available again. If this does not happen, turn the robot's power off, wait a few seconds, turn the power back on, and check the app again after the robot boots up.

1. After locating your robot in the app, click the three-dot menu (⋮), select **Robot settings**, and then click the **Networking** tab.

The Networking tab will show you the IP address and subnet mask of your robot. When disconnected from a network, Flex will assign itself a non-routing IP address. Here's an example of a self-assigned IP address on a Flex:

- IP address: 169.254.29.160
- Subnet mask: 255.255.0.0

#### Setting a static IP address

The static IP address on your computer needs to be in the same IP range and subnet that your Flex uses. Given the robot's IP address above, you could set your computer's IP address and subnet as shown here:

- IP address: 169.254.29.164
- Subnet mask: 255.255.0.0

After you have a working hardwired connection, follow the instructions in [Making an SSH Connection](software-operation.md#making-an-ssh-connection) above.

## Jupyter Notebook

Flex runs a [Jupyter Notebook](https://jupyter.org/) server on port 48888, which you can connect to with your web browser. Use Jupyter to individually run discrete chunks of Python code, called *cells*. This is a convenient environment for writing and debugging protocols, since you can define different parts of your protocol in different notebook cells, and run a single cell at a time.

Access your robot's Jupyter Notebook either:

- In the Opentrons App. Go to **Devices** > your robot > **Robot Settings** > **Advanced** and then click **Launch Jupyter Notebook**.

- In your web browser. Navigate directly to `http://<robot-ip>:48888`, replacing `<robot-ip>` with the local IP address of your Flex.

For more details on using Jupyter, including preparing executable cells
of code and running them on a robot, see the [Jupyter Notebook section](https://docs.opentrons.com/v2/new_advanced_running.html#jupyter-notebook) of the Python Protocol API documentation.

---
# Source: system-description.md
---

---
title: "Opentrons Flex: System Description"
---

# System Description

This chapter describes the hardware systems of Opentrons Flex, which underlie its core lab automation features. The deck, gantry, and instrument mounts of Opentrons Flex enable the use of precision liquid- and labware-handling components. The on-device touchscreen enables running protocols and checking on the robot's status without needing to bring your computer to the lab bench. Wired and wireless connectivity enables additional control from the Opentrons App (see the [Software and Operation chapter](software-operation.md) for more details) and extending the system's features by attaching peripherals (see the [Modules chapter](modules.md)).

## Physical components

<figure markdown>
![The frame, front door, and side windows enclose Flex. The deck is the inside bottom surface of the robot. The gantry runs across the working space of the robot. The status light is on the front top, and the touchscreen is on the front right. The internal camera is located in the top right corner. Handle caps are on the side of the robot on each outside bottom corner.](images/flex-physical-components.png "flex-physical-components.svg")
<figcaption>Locations of the physical components of Opentrons Flex.</figcaption>
</figure>

### Frame and enclosure

The *frame* of the Opentrons Flex robot provides rigidity and structural support for its deck and gantry. All of the mechanical subsystems are situated on and mounted to the main frame. The frame is constructed primarily of sheet metal and aluminum extrusions.

The metal frame has openings for *side windows* and a *front door* made of transparent polycarbonate that let you see what's going on inside Flex. The front door hinges open for access to the interior of the system. With the front door open, you can attach instruments, modules, and deck fixtures; prepare the deck before a protocol; or manipulate the state of the deck during a protocol.

White LED strips on the inside top edges of the frame provide software-controllable ambient lighting. A 2-megapixel camera can photograph the deck and working area for recording and tracking protocol execution.

### Deck and working area

The deck is the machined aluminum surface on which automated science protocols are executed. The deck has 12 main ANSI/SLAS-format slots that can be reconfigured to hold labware, modules, and consumables. The deck slots are identified by a coordinate system, with slot A1 at the back left and slot D3 at the front right.

<figure markdown>
![Areas of the deck within Flex.](images/deck-diagram.png "Areas of the deck within Flex")
<figcaption>Areas of the deck within Flex.</figcaption>
</figure>

The *working area* is the physical space above the deck that is accessible for pipetting. Labware placed in slots A1 through D3 are in the working area.

Opentrons Flex comes with *removable deck slots* for all 12 positions in the working area. Each deck slot has corner *labware clips* for securely placing labware on the deck.

You can reconfigure the deck by replacing slots with other *deck fixtures*, including the *movable trash, waste chute,* and *module caddies*. The *expansion slot* behind A1 is only used to make additional room for the Thermocycler Module, which occupies slots A1 and B1.

!!! note
    Deck slots are interchangeable within a column (1, 2, or 3) but not across columns; column 1 and column 3 slots are distinct pieces despite their similar size. You can tell which column a slot goes in by orienting the blue labware clip to the back left.

You should leave deck slots installed in locations where you want to place standalone labware. The deck and items placed on it remain static, unless moved by the gripper or manual intervention.

### Staging area

The *staging area* is additional space along the right side of the deck. You can store labware in this location after installing *staging area slots*. Labware placed in slots A4 through D4 are in the staging area. Flex pipettes cannot reach into the staging area, but the gripper can pick up and move labware to and from this location. Adding extra slots helps keep the working area available for the equipment used in your automated protocols.

Staging area slots are included in certain workstation configurations.
You can also purchase a [set of four slots](https://opentrons.com/products/opentrons-flex-deck-expansion-set-4-count) from Opentrons.

<figure markdown>
![Staging area slots in column 4.](images/deck-staging-area.png "Staging area slots")
<figcaption>Staging Area with Slots Installed</figcaption>
</figure>

### Deck fixtures

Fixtures are hardware items that replace standard deck slots. They let
you customize the deck layout and add functionality to your Flex.
Currently, deck fixtures include the staging area slots, the internal
trash bin, and the external waste chute. You can only install fixtures
in a few specific deck slots. The following table lists the deck
locations for each fixture.

| **Fixture**                        | **Slots**         |
|------------------------------------|-------------------|
| Staging area slots                 | A3–D3             |
| Trash bin                          | A1–D1 and A3–D3   |
| Waste chute                        | D3 only           |
| Waste chute with staging area slot | D3 only           |

Fixtures are unpowered. They do not contain electronic or mechanical components that communicate their current state and deck location to the robot. This means you have to use the deck configuration feature to let the Flex know what fixtures are attached to the deck and where they're located.

You can access the deck configuration settings from the touchscreen via the three-dot (⋮) menu and from the Opentrons App. See the [Deck Configuration section][deck-configuration] of the Software and Operation chapter for information on how to configure the deck from the touchscreen.

### Waste chute

The Opentrons Flex Waste Chute transfers liquids, tips, tip racks, and well plates from the Flex enclosure to a trash receptacle placed below its external opening. The waste chute attaches to a deck plate adapter that fits in slot D3. It also comes with a special window half panel that lets the chute extend out of the front of the robot.

<figure markdown>
![The waste chute, deck plate adapter, and deck plate adapter with staging area.](images/waste-chute-elements.png "Components of the waste chute")
<figcaption>Components of the waste chute.</figcaption>
</figure>

### Staging area slots

Staging area slots are ANSI/SLAS compatible deck pieces that replace standard slots in column 3 and add new slots to the staging area — all without losing space in the working area. You can install a single slot or a maximum of four slots to create a new column (A4 to D4) along the right side of the deck. Note, however, that replacing deck slot A3 requires moving the trash bin. By adding staging area slots to the deck, your Flex robot can store more labware and operate more efficiently.

<figure markdown>
![Flex staging area slot.](images/staging-slot.png "Flex staging area slot")
<figcaption>Flex staging area slot.</figcaption>
</figure>

#### Slot installation

To install, remove the screws that attach a standard slot to the deck and replace it with the staging area slot. After installation, use the touchscreen or Opentrons App to tell the robot you've added a staging area slot to the deck.

<figure markdown>
![Attachment points of the two staging slot screws. One is at the left edge of the slot and one is inside the right calibration square.](images/staging-slot-installation.svg "Staging slot screw locations")
<figcaption>Installing a staging area slot.</figcaption>
</figure>

#### Slot compatibility

Staging area slots are compatible with the Flex instruments, modules, and labware listed below.

| Flex component | Staging area compatibility |
|:-------------- |:------------|
| **Gripper**        | The Flex Gripper can move labware to or from staging area slots.                                                     |
| **Pipettes**       | Flex pipettes cannot reach the staging area. Use the gripper to move tip racks and labware from the staging area to the working area before pipetting. |
| **Modules**        | The Magnetic Block GEN1 can be placed in column 3 on top of a staging area slot. Modules are not supported in column 4.<br><br>Powered modules such as the Heater-Shaker and Temperature Module fit into caddies that can be placed in column 3. You can't add a staging area slot to a position occupied by a module caddy. |
| **Labware**        | Staging area slots have the same ANSI/SLAS dimensions as standard deck slots. Use in the staging area, or manually add and remove labware from this location. |

### Movement system

Attached to the frame is the *gantry*, which is the robot's movement and positioning system.

The gantry moves separately along the x- and y-axis to position the pipettes and gripper at precise locations for protocol execution. Movement along these axes is precise to the nearest 0.1 mm. The gantry is controlled by 36 VDC hybrid bipolar stepper motors.

In turn, attached to the gantry are the *pipette mounts* and the *extension mount*. These move along the z-axis to position the pipettes and gripper at precise locations for protocol execution. Movement along this axis is controlled by 36 VDC hybrid bipolar stepper motors.

The electronics contained in the gantry provide 36 VDC power and communications to the pipettes and gripper, when attached.

![Diagram of the horizontal gantry and its attached pipette and extension mounts.](images/gantry-diagram.svg "Gantry components")
Location of instrument mounts on Flex.

### Touchscreen and LED displays

The primary user interface is the 7-inch LCD *touchscreen*, located on the front right of the robot. The touchscreen is covered with Gorilla Glass 3 for scratch and damage resistance. Access many features of Flex right on the touchscreen, including:

- Protocol management

- Protocol setup, execution, and monitoring

- Labware management

- Robot settings

- System software and firmware updates

- Operation logs and error notifications

For more information on using Flex via the touchscreen, see the [Touchscreen Operation section](software-operation.md#touchscreen-operation) of the Software and Operation chapter.

The *status light* is a strip of LEDs along the top front of the robot that provides at-a-glance information about the robot. Different colors and patterns of illumination can communicate various success, failure, or idle states:

<table>
  <thead>
    <tr>
      <th>LED color</th>
      <th>LED pattern</th>
      <th>Robot status</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td rowspan="2" markdown>⚪️ White<br>Neutral states</td>
      <td>Solid</td>
      <td>Powered on and not running a protocol</td>
    </tr>
    <tr>
      <td>Pulsing</td>
      <td>Robot is busy (e.g., updating software or firmware, setting up protocol run, canceling protocol run)</td>
    </tr>
    <tr>
      <td rowspan="3">🟢 Green<br>Normal states</td>
      <td>Blinks twice</td>
      <td>Action is complete (e.g., protocol stored, software updated, instrument attached or detached)</td>
    </tr>
    <tr>
      <td>Solid</td>
      <td>Protocol is running</td>
    </tr>
    <tr>
      <td>Pulsing</td>
      <td>Protocol is complete</td>
    </tr>
    <tr>
      <td>🔵 Blue<br>Mandatory states</td>
      <td>Pulsing</td>
      <td>Protocol is paused</td>
    </tr>
    <tr>
      <td>🟡 Yellow<br>Abnormal states</td>
      <td>Solid</td>
      <td>Software error</td>
    </tr>
    <tr>
      <td>🔴 Red<br>Emergency states</td>
      <td>Blinks three times, repeatedly</td>
      <td>Physical error (e.g., instrument crash)</td>
    </tr>
  </tbody>
</table>

The status light can also be disabled in the robot settings.

## Pipettes

Opentrons *pipettes* are configurable devices used to move liquids throughout the working area during the execution of protocols. There are several Opentrons Flex pipettes, which can handle volumes from 1 µL to 1000 µL in 1, 8, or 96 channels:

- Opentrons Flex 1-Channel Pipette (1–50 µL)

- Opentrons Flex 1-Channel Pipette (5–1000 µL)

- Opentrons Flex 8-Channel Pipette (1–50 µL)

- Opentrons Flex 8-Channel Pipette (5–1000 µL)

- Opentrons Flex 96-Channel Pipette (5–1000 µL)

Pipettes attach to the gantry using captive screws on the front of the pipette. 1-channel and 8-channel pipettes each occupy one *pipette mount* (left or right); the 96-channel pipette occupies both mounts. For details on installing pipettes, see [Instrument Installation and Calibration][instrument-installation-and-calibration].

![Each capacity of pipette has captive attachment screws on its front. Pipette ejectors are at the bottom of each pipette, above the nozzles. The 1- and 8-channel pipettes have replaceable O-rings, and the 96-channel pipette has fixed O-rings.](images/pipette-components.png "Pipette components")
Locations of components of the 1-, 8-, and 96-channel pipettes.

The pipettes pick up disposable plastic *tips* by pressing them onto the pipette *nozzles*, and then use the tips to aspirate and dispense liquids. The amount of total force required for pickup increases as more tips get picked up simultaneously. For smaller numbers of tips, the pipette attaches tips by pushing each pipette nozzle down into a tip. To achieve the necessary force to pick up a full rack of tips, the 96-channel pipette also pulls the tips upward onto the nozzles. This pulling action requires placing tip racks into a *tip rack adapter*, rather than directly in a deck slot. To discard tips (or return them to their rack), the pipette *ejector* mechanism pushes the tips off of the nozzles.

### Pipette specifications

Opentrons Flex pipettes are designed to handle a wide range of volumes.
Because of their wide overall range, they can use multiple sizes of tips, which affect their liquid-handling characteristics. Opentrons has tested Flex pipettes for accuracy and precision in a number of tip and liquid volume combinations:

<table>
  <thead>
    <tr>
      <th>Pipette</th>
      <th>Tip Capacity</th>
      <th>Tested Volume</th>
      <th>Accuracy %D</th>
      <th>Precision %CV</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td rowspan="3"><b>Flex 1-Channel 50 µL</b></td>
      <td>50 µL</td>
      <td>1 µL</td>
      <td>8.00%</td>
      <td>7.00%</td>
    </tr>
    <tr>
      <td>50 µL</td>
      <td>10 µL</td>
      <td>1.50%</td>
      <td>0.50%</td>
    </tr>
    <tr>
      <td>50 µL</td>
      <td>50 µL</td>
      <td>1.25%</td>
      <td>0.40%</td>
    </tr>
    <tr>
      <td rowspan="4"><b>Flex 1-Channel 1000 µL</b></td>
      <td>50 µL</td>
      <td>5 µL</td>
      <td>5.00%</td>
      <td>2.50%</td>
    </tr>
    <tr>
      <td>50 µL</td>
      <td>50 µL</td>
      <td>0.50%</td>
      <td>0.30%</td>
    </tr>
    <tr>
      <td>200 µL</td>
      <td>200 µL</td>
      <td>0.50%</td>
      <td>0.15%</td>
    </tr>
    <tr>
      <td>1000 µL</td>
      <td>1000 µL</td>
      <td>0.50%</td>
      <td>0.15%</td>
    </tr>
    <tr>
      <td rowspan="3"><b>Flex 8-Channel 50 µL</b></td>
      <td>50 µL</td>
      <td>1 µL</td>
      <td>10.00%</td>
      <td>8.00%</td>
    </tr>
    <tr>
      <td>50 µL</td>
      <td>10 µL</td>
      <td>2.50%</td>
      <td>1.00%</td>
    </tr>
    <tr>
      <td>50 µL</td>
      <td>50 µL</td>
      <td>1.25%</td>
      <td>0.60%</td>
    </tr>
    <tr>
      <td rowspan="4"><b>Flex 8-Channel 1000 µL</b></td>
      <td>50 µL</td>
      <td>5 µL</td>
      <td>8.00%</td>
      <td>4.00%</td>
    </tr>
    <tr>
      <td>50 µL</td>
      <td>50 µL</td>
      <td>2.50%</td>
      <td>0.60%</td>
    </tr>
    <tr>
      <td>200 µL</td>
      <td>200 µL</td>
      <td>1.00%</td>
      <td>0.25%</td>
    </tr>
    <tr>
      <td>1000 µL</td>
      <td>1000 µL</td>
      <td>0.70%</td>
      <td>0.15%</td>
    </tr>
    <tr>
      <td rowspan="4"><b>Flex 96-Channel 1000 µL</b></td>
      <td>50 µL</td>
      <td>5 µL</td>
      <td>10.00%</td>
      <td>5.00%</td>
    </tr>
    <tr>
      <td>50 µL</td>
      <td>50 µL</td>
      <td>2.50%</td>
      <td>1.25%</td>
    </tr>
    <tr>
      <td>200 µL</td>
      <td>200 µL</td>
      <td>1.50%</td>
      <td>1.25%</td>
    </tr>
    <tr>
      <td>1000 µL</td>
      <td>1000 µL</td>
      <td>1.50%</td>
      <td>1.50%</td>
    </tr>
  </tbody>
</table>

Keep this accuracy information in mind when choosing tips for your
pipette. In general, for best results you should use the smallest tips
that meet the needs of your protocol.

!!! note
    Opentrons performs volumetric testing of Flex pipettes to ensure that they meet the accuracy and precision specifications listed above. You *do not* have to calibrate the volume that your pipettes dispense before use. You only have to perform positional calibration. See the next section, as well as the [Pipette Installation section][pipette-installation] of the Installation and Relocation chapter, for details.

    The Opentrons Care and Opentrons Care Plus services include yearly pipette replacement and certificates of calibration. See the [Servicing Flex section][servicing-flex] of the Maintenance and Service chapter for details.

### Pipette calibration

The User Kit includes a metal pipette calibration probe, which you use during positional calibration. During protocol runs, safely store the probe on the magnetic holder on the front pillar of the robot. During the calibration process, attach the probe to the appropriate nozzle and lock it in place. The robot moves the probe to calibration points on the deck to measure the pipette's exact position.

### Pipette tip rack adapter

![The 96-channel tip rack adapter.](images/96-channel-tip-rack-adapter.png "96-channel tip rack adapter")

The Opentrons Flex 96-channel pipette ships with four tip rack adapters. These are precision formed aluminum brackets that you place on the deck. The adapters hold Flex 50 μL, 200 μL, and 1000 µL tip racks.

Because of the force involved, the 96-channel pipette requires an adapter to attach a full tip rack properly. During the attachment procedure, the pipette moves over the adapter, lowers itself onto the mounting pins, and pulls tips onto the pipettes by lifting the adapter and tip rack. Pulling the tips, rather than pushing, provides the leverage needed to secure tips to the pipettes and prevents warping the deck surface. When finished, the 96-channel pipette lowers the adapter and empty tip rack onto the deck. See the [Tips and Tip Racks section][tips-and-tip-racks] of the Labware chapter for more information.

### Partial tip pickup

By default, multi-channel pipettes use all of their nozzles to pick up tips and handle liquids: an 8-channel pipette picks up 8 tips at once, and a 96-channel pipette picks up 96 tips at once. Partial tip pickup lets you configure a multi-channel pipette to use fewer tips. This expands the liquid handling capabilities of your robot without having to physically switch pipettes, and is especially useful for the 96-channel pipette, which occupies both pipette mounts.

Currently, the 96-channel pipette supports partial tip pickup for a column, a row, or a single tip. The 8-channel pipettes support a partial column (2–7 consecutive tips) or a single tip.

When picking up fewer than 96 tips from a tip rack with any pipette, the rack must be placed directly on the deck, not in the tip rack adapter.

### Pipette sensors

Opentrons Flex pipettes have a number of sensors that detect and record data about the status of the pipette and any tips it has picked up.

#### Capacitance sensors

In combination with a metal probe or conductive tip, the capacitance sensors detect when the pipette makes contact with something. Detection of contact between the metal probe and the deck is used in the automated [pipette calibration][pipette-calibration] and [module calibration][module-calibration] processes.

1-channel pipettes have one capacitance sensor, while multi-channel pipettes have two: on channels 1 and 8 of 8-channel pipettes, and on channels 1 and 96 (positions A1 and H12) of the 96-channel pipette.

#### Optical tip presence sensors

A photointerruptor switch detects the position of the pipette's tip ejector mechanism, confirming whether tips were successfully picked up or dropped. 1-channel, 8-channel, and 96-channel pipettes all have a single optical sensor that monitors tip attachment across all channels.

#### Pressure sensors

Flex pipettes use internal pressure sensors to detect liquid in well plates, reservoirs, and tubes. Liquid detection takes place as a pipette approaches the surface of a liquid. Sensors in the pipettes detect pressure changes relative to ambient pressure. A particular change in pressure tells the robot that liquid is present in a well and the pipette tip is in contact with the liquid's surface.

1-channel pipettes have one pressure sensor. The 8-channel pipette pressure sensors are on channels 1 and 8 (positions A1 and H1). The 96-channel pipette pressure sensors are on channels 1 and 96 (positions A1 and H12). Other channels on multi-channel pipettes do not have sensors and cannot detect liquid.
