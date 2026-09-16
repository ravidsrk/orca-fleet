# Frozen obligation catalog — NIST-SP-800-218@1.0.0

SOURCE (bytes frozen in this dir as NIST_SP800-218_ver1_catalog.json):
- URL: https://raw.githubusercontent.com/usnistgov/oscal-content/main/nist.gov/SP800-218/ver1/json/NIST_SP800-218_ver1_catalog.json
- upstream commit: 78650f02ad9321bb7b817846f8fbd4f2bcd620de (2026-05-13, oscalbuilder bot)
- git blob sha: 94f85f214557d4f52faddbf0b2e83de55d11db5d
- bytes sha256: b01634a5fdb382e7a12660c379a4d0bc3a2b8e29abccf2861834880005137117 (253878 bytes)
- read date: 2026-09-16
- unit: one SSDF task; denominator = 42 tasks; frozen — the run cannot shrink it.

## PO.1.1 — PO.1 Define Security Requirements for Software Development
**Statement:** Identify and document all security requirements for the organization’s software development infrastructures and processes, and maintain the requirements over time.
- Ex1: Define policies for securing software development infrastructures and their components, including development endpoints, throughout the SDLC and maintaining that security.
- Ex2: Define policies for securing software development processes throughout the SDLC and maintaining that security, including for open-source and other third-party software components utilized by software being developed.
- Ex3: Review and update security requirements at least annually, or sooner if there are new requirements from internal or external sources, or a major security incident targeting software development infrastructure has occurred.
- Ex4: Educate affected individuals on impending changes to requirements.

## PO.1.2 — PO.1 Define Security Requirements for Software Development
**Statement:** Identify and document all security requirements for organization-developed software to meet, and maintain the requirements over time.
- Ex1: Define policies that specify risk-based software architecture and design requirements, such as making code modular to facilitate code reuse and updates; isolating security components from other components during execution; avoiding undocumented commands and settings; and providing features that will aid software acquirers with the secure deployment, operation, and maintenance of the software.
- Ex2: Define policies that specify the security requirements for the organization’s software, and verify compliance at key points in the SDLC (e.g., classes of software flaws verified by gates, responses to vulnerabilities discovered in released software).
- Ex3: Analyze the risk of applicable technology stacks (e.g., languages, environments, deployment models), and recommend or require the use of stacks that will reduce risk compared to others.
- Ex4: Define policies that specify what needs to be archived for each software release (e.g., code, package files, third-party libraries, documentation, data inventory) and how long it needs to be retained based on the SDLC model, software end-of-life, and other factors.
- Ex5: Ensure that policies cover the entire software life cycle, including notifying users of the impending end of software support and the date of software end-of-life.
- Ex6: Review all security requirements at least annually, or sooner if there are new requirements from internal or external sources, a major vulnerability is discovered in released software, or a major security incident targeting organization-developed software has occurred.
- Ex7: Establish and follow processes for handling requirement exception requests, including periodic reviews of all approved exceptions.

## PO.1.3 — PO.1 Define Security Requirements for Software Development
**Statement:** Communicate requirements to all third parties who will provide commercial software components to the organization for reuse by the organization’s own software. .Formerly PW.3.1
- Ex1: Define a core set of security requirements for software components, and include it in acquisition documents, software contracts, and other agreements with third parties.
- Ex2: Define security-related criteria for selecting software; the criteria can include the third party’s vulnerability disclosure program and product security incident response capabilities or the third party’s adherence to organization-defined practices.
- Ex3: Require third parties to attest that their software complies with the organization’s security requirements.
- Ex4: Require third parties to provide provenance data and integrity verification mechanisms for all components of their software.
- Ex5: Establish and follow processes to address risk when there are security requirements that third-party software components to be acquired do not meet; this should include periodic reviews of all approved exceptions to requirements.

## PO.2.1 — PO.2 Implement Roles and Responsibilities
**Statement:** Create new roles and alter responsibilities for existing roles as needed to encompass all parts of the SDLC. Periodically review and maintain the defined roles and responsibilities, updating them as needed.
- Ex1: Define SDLC-related roles and responsibilities for all members of the software development team.
- Ex2: Integrate the security roles into the software development team.
- Ex3: Define roles and responsibilities for cybersecurity staff, security champions, project managers and leads, senior management, software developers, software testers, software assurance leads and staff, product owners, operations and platform engineers, and others involved in the SDLC.
- Ex4: Conduct an annual review of all roles and responsibilities.
- Ex5: Educate affected individuals on impending changes to roles and responsibilities, and confirm that the individuals understand the changes and agree to follow them.
- Ex6: Implement and use tools and processes to promote communication and engagement among individuals with SDLC-related roles and responsibilities, such as creating messaging channels for team discussions.
- Ex7: Designate a group of individuals or a team as the code owner for each project.

## PO.2.2 — PO.2 Implement Roles and Responsibilities
**Statement:** Provide role-based training for all personnel with responsibilities that contribute to secure development. Periodically review personnel proficiency and role-based training, and update the training as needed.
- Ex1: Document the desired outcomes of training for each role.
- Ex2: Define the type of training or curriculum required to achieve the desired outcome for each role.
- Ex3: Create a training plan for each role.
- Ex4: Acquire or create training for each role; acquired training may need to be customized for the organization.
- Ex5: Measure outcome performance to identify areas where changes to training may be beneficial.

## PO.2.3 — PO.2 Implement Roles and Responsibilities
**Statement:** Obtain upper management or authorizing official commitment to secure development, and convey that commitment to all with development-related roles and responsibilities.
- Ex1: Appoint a single leader or leadership team to be responsible for the entire secure software development process, including being accountable for releasing software to production and delegating responsibilities as appropriate.
- Ex2: Increase authorizing officials’ awareness of the risks of developing software without integrating security throughout the development life cycle and the risk mitigation provided by secure development practices.
- Ex3: Assist upper management in incorporating secure development support into their communications with personnel with development-related roles and responsibilities.
- Ex4: Educate all personnel with development-related roles and responsibilities on upper management’s commitment to secure development and the importance of secure development to the organization.

## PO.3.1 — PO.3 Implement Supporting Toolchains
**Statement:** Specify which tools or tool types must or should be included in each toolchain to mitigate identified risks, as well as how the toolchain components are to be integrated with each other.
- Ex1: Define categories of toolchains, and specify the mandatory tools or tool types to be used for each category.
- Ex2: Identify security tools to integrate into the developer toolchain.
- Ex3: Define what information is to be passed between tools and what data formats are to be used.
- Ex4: Evaluate tools’ signing capabilities to create immutable records/logs for auditability within the toolchain.
- Ex5: Use automated technology for toolchain management and orchestration.

## PO.3.2 — PO.3 Implement Supporting Toolchains
**Statement:** Follow recommended security practices to deploy, operate, and maintain tools and toolchains.
- Ex1: Evaluate, select, and acquire tools, and assess the security of each tool.
- Ex2: Integrate tools with other tools and existing software development processes and workflows.
- Ex3: Use code-based configuration for toolchains (e.g., pipelines-as-code, toolchains-as-code).
- Ex4: Implement the technologies and processes needed for reproducible builds.
- Ex5: Update, upgrade, or replace tools as needed to address tool vulnerabilities or add new tool capabilities.
- Ex6: Continuously monitor tools and tool logs for potential operational and security issues, including policy violations and anomalous behavior.
- Ex7: Regularly verify the integrity and check the provenance of each tool to identify potential problems.
- Ex8: See PW.6 regarding compiler, interpreter, and build tools.
- Ex9: See PO.5 regarding implementing and maintaining secure environments.

## PO.3.3 — PO.3 Implement Supporting Toolchains
**Statement:** Configure tools to generate artifacts of their support of secure software development practices as defined by the organization.
- Ex1: Use existing tooling (e.g., workflow tracking, issue tracking, value stream mapping) to create an audit trail of the secure development-related actions that are performed for continuous improvement purposes.
- Ex2: Determine how often the collected information should be audited, and implement the necessary processes.
- Ex3: Establish and enforce security and retention policies for artifact data.
- Ex4: Assign responsibility for creating any needed artifacts that tools cannot generate.

## PO.4.1 — PO.4 Define and Use Criteria for Software Security Checks
**Statement:** Define criteria for software security checks and track throughout the SDLC.
- Ex1: Ensure that the criteria adequately indicate how effectively security risk is being managed.
- Ex2: Define key performance indicators (KPIs), key risk indicators (KRIs), vulnerability severity scores, and other measures for software security.
- Ex3: Add software security criteria to existing checks (e.g., the Definition of Done in agile SDLC methodologies).
- Ex4: Review the artifacts generated as part of the software development workflow system to determine if they meet the criteria.
- Ex5: Record security check approvals, rejections, and exception requests as part of the workflow and tracking system.
- Ex6: Analyze collected data in the context of the security successes and failures of each development project, and use the results to improve the SDLC.

## PO.4.2 — PO.4 Define and Use Criteria for Software Security Checks
**Statement:** Implement processes, mechanisms, etc. to gather and safeguard the necessary information in support of the criteria.
- Ex1: Use the toolchain to automatically gather information that informs security decision-making.
- Ex2: Deploy additional tools if needed to support the generation and collection of information supporting the criteria.
- Ex3: Automate decision-making processes utilizing the criteria, and periodically review these processes.
- Ex4: Only allow authorized personnel to access the gathered information, and prevent any alteration or deletion of the information.

## PO.5.1 — PO.5 Implement and Maintain Secure Environments for Software Development
**Statement:** Separate and protect each environment involved in software development.
- Ex1: Use multi-factor, risk-based authentication and conditional access for each environment.
- Ex2: Configure and implement measures to secure the environments’ hosting infrastructures following a zero trust architecture.
- Ex3: Use network segmentation and access controls to separate the environments from each other and from production environments, and to separate components from each other within each non-production environment, in order to reduce attack surfaces and attackers’ lateral movement and privilege/access escalation.
- Ex4: Enforce authentication and tightly restrict connections entering and exiting each software development environment, including minimizing access to the internet to only what is necessary.
- Ex5: Minimize direct human access to toolchain systems, such as build services. Continuously monitor and audit all access attempts and all use of privileged access.
- Ex6: Minimize the use of production-environment software and services from non-production environments.
- Ex7: Regularly log, monitor, and audit trust relationships for authorization and access between the environments and between the components within each environment.
- Ex8: Continuously log and monitor operations and alerts across all components of the development environment to detect, respond, and recover from attempted and actual cyber incidents.
- Ex9: Configure security controls and other tools involved in separating and protecting the environments to generate artifacts for their activities.
- Ex10: Continuously monitor all software deployed in each environment for new vulnerabilities, and respond to vulnerabilities appropriately following a risk-based approach.

## PO.5.2 — PO.5 Implement and Maintain Secure Environments for Software Development
**Statement:** Secure and harden development endpoints (i.e., endpoints for software designers, developers, testers, builders, etc.) to perform development-related tasks using a risk-based approach.
- Ex1: Configure each development endpoint based on approved hardening guides, checklists, etc.; for example, enable FIPS-compliant encryption of all sensitive data at rest and in transit.
- Ex2: Configure each development endpoint and the development resources to provide the least functionality needed by users and services and to enforce the principle of least privilege.
- Ex3: Continuously monitor the security posture of all development endpoints, including monitoring and auditing all use of privileged access.
- Ex4: Configure security controls and other tools involved in securing and hardening development endpoints to generate artifacts for their activities.
- Ex5: Require multi-factor authentication for all access to development endpoints and development resources.
- Ex6: Provide dedicated development endpoints on non-production networks for performing all development-related tasks. Provide separate endpoints on production networks for all other tasks.
- Ex7: Configure each development endpoint following a zero trust architecture.

## PS.1.1 — PS.1 Protect All Forms of Code from Unauthorized Access and Tampering
**Statement:** Store all forms of code – including source code, executable code, and configuration-as-code – based on the principle of least privilege so that only authorized personnel, tools, services, etc. have access.
- Ex1: Store all source code and configuration-as-code in a code repository, and restrict access to it based on the nature of the code. For example, open-source code intended for public access may need its integrity and availability protected; other code may also need its confidentiality protected.
- Ex2: Use version control features of the repository to track all changes made to the code with accountability to the individual account.
- Ex3: Use commit signing for code repositories.
- Ex4: Have the code owner review and approve all changes made to the code by others.
- Ex5: Use code signing to help protect the integrity of executables.
- Ex6: Use cryptography (e.g., cryptographic hashes) to help protect file integrity.

## PS.2.1 — PS.2 Provide a Mechanism for Verifying Software Release Integrity
**Statement:** Make software integrity verification information available to software acquirers.
- Ex1: Post cryptographic hashes for release files on a well-secured website.
- Ex2: Use an established certificate authority for code signing so that consumers’ operating systems or other tools and services can confirm the validity of signatures before use.
- Ex3: Periodically review the code signing processes, including certificate renewal, rotation, revocation, and protection.

## PS.3.1 — PS.3 Archive and Protect Each Software Release
**Statement:** Securely archive the necessary files and supporting data (e.g., integrity verification information, provenance data) to be retained for each software release.
- Ex1: Store the release files, associated images, etc. in repositories following the organization’s established policy. Allow read-only access to them by necessary personnel and no access by anyone else.
- Ex2: Store and protect release integrity verification information and provenance data, such as by keeping it in a separate location from the release files or by signing the data.

## PS.3.2 — PS.3 Archive and Protect Each Software Release
**Statement:** Collect, safeguard, maintain, and share provenance data for all components of each software release (e.g., in a software bill of materials .SBOM).
- Ex1: Make the provenance data available to software acquirers in accordance with the organization’s policies, preferably using standards-based formats.
- Ex2: Make the provenance data available to the organization’s operations and response teams to aid them in mitigating software vulnerabilities.
- Ex3: Protect the integrity of provenance data, and provide a way for recipients to verify provenance data integrity.
- Ex4: Update the provenance data every time any of the software’s components are updated.

## PW.1.1 — PW.1 Design Software to Meet Security Requirements and Mitigate Security Risks
**Statement:** Use forms of risk modeling – such as threat modeling, attack modeling, or attack surface mapping – to help assess the security risk for the software.
- Ex1: Train the development team (security champions, in particular) or collaborate with a risk modeling expert to create models and analyze how to use a risk-based approach to communicate the risks and determine how to address them, including implementing mitigations.
- Ex2: Perform more rigorous assessments for high-risk areas, such as protecting sensitive data and safeguarding identification, authentication, and access control, including credential management.
- Ex3: Review vulnerability reports and statistics for previous software to inform the security risk assessment.
- Ex4: Use data classification methods to identify and characterize each type of data that the software will interact with.

## PW.1.2 — PW.1 Design Software to Meet Security Requirements and Mitigate Security Risks
**Statement:** Track and maintain the software’s security requirements, risks, and design decisions.
- Ex1: Record the response to each risk, including how mitigations are to be achieved and what the rationales are for any approved exceptions to the security requirements. Add any mitigations to the software’s security requirements.
- Ex2: Maintain records of design decisions, risk responses, and approved exceptions that can be used for auditing and maintenance purposes throughout the rest of the software life cycle.
- Ex3: Periodically re-evaluate all approved exceptions to the security requirements, and implement changes as needed.

## PW.1.3 — PW.1 Design Software to Meet Security Requirements and Mitigate Security Risks
**Statement:** Where appropriate, build in support for using standardized security features and services (e.g., enabling software to integrate with existing log management, identity management, access control, and vulnerability management systems) instead of creating proprietary implementations of security features and services. .Formerly PW.4.3
- Ex1: Maintain one or more software repositories of modules for supporting standardized security features and services.
- Ex2: Determine secure configurations for modules for supporting standardized security features and services, and make these configurations available (e.g., as configuration-as-code) so developers can readily use them.
- Ex3: Define criteria for which security features and services must be supported by software to be developed.

## PW.2.1 — PW.2 Review the Software Design to Verify Compliance with Security Requirements and Risk Information
**Statement:** Have 1) a qualified person (or people) who were not involved with the design and/or 2) automated processes instantiated in the toolchain review the software design to confirm and enforce that it meets all of the security requirements and satisfactorily addresses the identified risk information.
- Ex1: Review the software design to confirm that it addresses applicable security requirements.
- Ex2: Review the risk models created during software design to determine if they appear to adequately identify the risks.
- Ex3: Review the software design to confirm that it satisfactorily addresses the risks identified by the risk models.
- Ex4: Have the software’s designer correct failures to meet the requirements.
- Ex5: Change the design and/or the risk response strategy if the security requirements cannot be met.
- Ex6: Record the findings of design reviews to serve as artifacts (e.g., in the software specification, in the issue tracking system, in the threat model).

## PW.4.1 — PW.4 Reuse Existing, Well-Secured Software When Feasible Instead of Duplicating Functionality
**Statement:** Acquire and maintain well-secured software components (e.g., software libraries, modules, middleware, frameworks) from commercial, open-source, and other third-party developers for use by the organization’s software.
- Ex1: Review and evaluate third-party software components in the context of their expected use. If a component is to be used in a substantially different way in the future, perform the review and evaluation again with that new context in mind.
- Ex2: Determine secure configurations for software components, and make these available (e.g., as configuration-as-code) so developers can readily use the configurations.
- Ex3: Obtain provenance information (e.g., SBOM, source composition analysis, binary software composition analysis) for each software component, and analyze that information to better assess the risk that the component may introduce.
- Ex4: Establish one or more software repositories to host sanctioned and vetted open-source components.
- Ex5: Maintain a list of organization-approved commercial software components and component versions along with their provenance data.
- Ex6: Designate which components must be included in software to be developed.
- Ex7: Implement processes to update deployed software components to newer versions, and retain older versions of software components until all transitions from those versions have been completed successfully.
- Ex8: If the integrity or provenance of acquired binaries cannot be confirmed, build binaries from source code after verifying the source code’s integrity and provenance.

## PW.4.2 — PW.4 Reuse Existing, Well-Secured Software When Feasible Instead of Duplicating Functionality
**Statement:** Create and maintain well-secured software components in-house following SDLC processes to meet common internal software development needs that cannot be better met by third-party software components.
- Ex1: Follow organization-established security practices for secure software development when creating and maintaining the components.
- Ex2: Determine secure configurations for software components, and make these available (e.g., as configuration-as-code) so developers can readily use the configurations.
- Ex3: Maintain one or more software repositories for these components.
- Ex4: Designate which components must be included in software to be developed.
- Ex5: Implement processes to update deployed software components to newer versions, and maintain older versions of software components until all transitions from those versions have been completed successfully.

## PW.4.4 — PW.4 Reuse Existing, Well-Secured Software When Feasible Instead of Duplicating Functionality
**Statement:** Verify that acquired commercial, open-source, and all other third-party software components comply with the requirements, as defined by the organization, throughout their life cycles.
- Ex1: Regularly check whether there are publicly known vulnerabilities in the software modules and services that vendors have not yet fixed.
- Ex2: Build into the toolchain automatic detection of known vulnerabilities in software components.
- Ex3: Use existing results from commercial services for vetting the software modules and services.
- Ex4: Ensure that each software component is still actively maintained and has not reached end of life; this should include new vulnerabilities found in the software being remediated.
- Ex5: Determine a plan of action for each software component that is no longer being maintained or will not be available in the near future.
- Ex6: Confirm the integrity of software components through digital signatures or other mechanisms.
- Ex7: Review, analyze, and/or test code. See PW.7 and PW.8.

## PW.5.1 — PW.5 Create Source Code by Adhering to Secure Coding Practices
**Statement:** Follow all secure coding practices that are appropriate to the development languages and environment to meet the organization’s requirements.
- Ex1: Validate all inputs, and validate and properly encode all outputs.
- Ex2: Avoid using unsafe functions and calls.
- Ex3: Detect errors, and handle them gracefully.
- Ex4: Provide logging and tracing capabilities.
- Ex5: Use development environments with automated features that encourage or require the use of secure coding practices with just-in-time training-in-place.
- Ex6: Follow procedures for manually ensuring compliance with secure coding practices when automated methods are insufficient or unavailable.
- Ex7: Use tools (e.g., linters, formatters) to standardize the style and formatting of the source code.
- Ex8: Check for other vulnerabilities that are common to the development languages and environment.
- Ex9: Have the developer review their own human-readable code to complement (not replace) code review performed by other people or tools. See PW.7.

## PW.6.1 — PW.6 Configure the Compilation, Interpreter, and Build Processes to Improve Executable Security
**Statement:** Use compiler, interpreter, and build tools that offer features to improve executable security.
- Ex1: Use up-to-date versions of compiler, interpreter, and build tools.
- Ex2: Follow change management processes when deploying or updating compiler, interpreter, and build tools, and audit all unexpected changes to tools.
- Ex3: Regularly validate the authenticity and integrity of compiler, interpreter, and build tools. See PO.3.

## PW.6.2 — PW.6 Configure the Compilation, Interpreter, and Build Processes to Improve Executable Security
**Statement:** Determine which compiler, interpreter, and build tool features should be used and how each should be configured, then implement and use the approved configurations.
- Ex1: Enable compiler features that produce warnings for poorly secured code during the compilation process.
- Ex2: Implement the “clean build” concept, where all compiler warnings are treated as errors and eliminated except those determined to be false positives or irrelevant.
- Ex3: Perform all builds in a dedicated, highly controlled build environment.
- Ex4: Enable compiler features that randomize or obfuscate execution characteristics, such as memory location usage, that would otherwise be predictable and thus potentially exploitable.
- Ex5: Test to ensure that the features are working as expected and are not inadvertently causing any operational issues or other problems.
- Ex6: Continuously verify that the approved configurations are being used.
- Ex7: Make the approved tool configurations available as configuration-as-code so developers can readily use them.

## PW.7.1 — PW.7 Review and/or Analyze Human-Readable Code to Identify Vulnerabilities and Verify Compliance with Security Requirements
**Statement:** Determine whether code review (a person looks directly at the code to find issues) and/or code analysis (tools are used to find issues in code, either in a fully automated way or in conjunction with a person) should be used, as defined by the organization.
- Ex1: Follow the organization’s policies or guidelines for when code review should be performed and how it should be conducted. This may include third-party code and reusable code modules written in-house.
- Ex2: Follow the organization’s policies or guidelines for when code analysis should be performed and how it should be conducted.
- Ex3: Choose code review and/or analysis methods based on the stage of the software.

## PW.7.2 — PW.7 Review and/or Analyze Human-Readable Code to Identify Vulnerabilities and Verify Compliance with Security Requirements
**Statement:** Perform the code review and/or code analysis based on the organization’s secure coding standards, and record and triage all discovered issues and recommended remediations in the development team’s workflow or issue tracking system.
- Ex1: Perform peer review of code, and review any existing code review, analysis, or testing results as part of the peer review.
- Ex2: Use expert reviewers to check code for backdoors and other malicious content.
- Ex3: Use peer reviewing tools that facilitate the peer review process, and document all discussions and other feedback.
- Ex4: Use a static analysis tool to automatically check code for vulnerabilities and compliance with the organization’s secure coding standards with a human reviewing the issues reported by the tool and remediating them as necessary.
- Ex5: Use review checklists to verify that the code complies with the requirements.
- Ex6: Use automated tools to identify and remediate documented and verified unsafe software practices on a continuous basis as human-readable code is checked into the code repository.
- Ex7: Identify and document the root causes of discovered issues.
- Ex8: Document lessons learned from code review and analysis in a wiki that developers can access and search.

## PW.8.1 — PW.8 Test Executable Code to Identify Vulnerabilities and Verify Compliance with Security Requirements
**Statement:** Determine whether executable code testing should be performed to find vulnerabilities not identified by previous reviews, analysis, or testing and, if so, which types of testing should be used.
- Ex1: Follow the organization’s policies or guidelines for when code testing should be performed and how it should be conducted (e.g., within a sandboxed environment). This may include third-party executable code and reusable executable code modules written in-house.
- Ex2: Choose testing methods based on the stage of the software.

## PW.8.2 — PW.8 Test Executable Code to Identify Vulnerabilities and Verify Compliance with Security Requirements
**Statement:** Scope the testing, design the tests, perform the testing, and document the results, including recording and triaging all discovered issues and recommended remediations in the development team’s workflow or issue tracking system.
- Ex1: Perform robust functional testing of security features.
- Ex2: Integrate dynamic vulnerability testing into the project’s automated test suite.
- Ex3: Incorporate tests for previously reported vulnerabilities into the project’s test suite to ensure that errors are not reintroduced.
- Ex4: Take into consideration the infrastructures and technology stacks that the software will be used with in production when developing test plans.
- Ex5: Use fuzz testing tools to find issues with input handling.
- Ex6: If resources are available, use penetration testing to simulate how an attacker might attempt to compromise the software in high-risk scenarios.
- Ex7: Identify and record the root causes of discovered issues.
- Ex8: Document lessons learned from code testing in a wiki that developers can access and search.
- Ex9: Use source code, design records, and other resources when developing test plans.

## PW.9.1 — PW.9 Configure Software to Have Secure Settings by Default
**Statement:** Define a secure baseline by determining how to configure each setting that has an effect on security or a security-related setting so that the default settings are secure and do not weaken the security functions provided by the platform, network infrastructure, or services.
- Ex1: Conduct testing to ensure that the settings, including the default settings, are working as expected and are not inadvertently causing any security weaknesses, operational issues, or other problems.

## PW.9.2 — PW.9 Configure Software to Have Secure Settings by Default
**Statement:** Implement the default settings (or groups of default settings, if applicable), and document each setting for software administrators.
- Ex1: Verify that the approved configuration is in place for the software.
- Ex2: Document each setting’s purpose, options, default value, security relevance, potential operational impact, and relationships with other settings.
- Ex3: Use authoritative programmatic technical mechanisms to record how each setting can be implemented and assessed by software administrators.
- Ex4: Store the default configuration in a usable format and follow change control practices for modifying it (e.g., configuration-as-code).

## RV.1.1 — RV.1 Identify and Confirm Vulnerabilities on an Ongoing Basis
**Statement:** Gather information from software acquirers, users, and public sources on potential vulnerabilities in the software and third-party components that the software uses, and investigate all credible reports.
- Ex1: Monitor vulnerability databases , security mailing lists, and other sources of vulnerability reports through manual or automated means.
- Ex2: Use threat intelligence sources to better understand how vulnerabilities in general are being exploited.
- Ex3: Automatically review provenance and software composition data for all software components to identify any new vulnerabilities they have.

## RV.1.2 — RV.1 Identify and Confirm Vulnerabilities on an Ongoing Basis
**Statement:** Review, analyze, and/or test the software’s code to identify or confirm the presence of previously undetected vulnerabilities.
- Ex1: Configure the toolchain to perform automated code analysis and testing on a regular or continuous basis for all supported releases.
- Ex2: See PW.7 and PW.8.

## RV.1.3 — RV.1 Identify and Confirm Vulnerabilities on an Ongoing Basis
**Statement:** Have a policy that addresses vulnerability disclosure and remediation, and implement the roles, responsibilities, and processes needed to support that policy.
- Ex1: Establish a vulnerability disclosure program, and make it easy for security researchers to learn about your program and report possible vulnerabilities.
- Ex2: Have a Product Security Incident Response Team (PSIRT) and processes in place to handle the responses to vulnerability reports and incidents, including communications plans for all stakeholders.
- Ex3: Have a security response playbook to handle a generic reported vulnerability, a report of zero-days, a vulnerability being exploited in the wild, and a major ongoing incident involving multiple parties and open-source software components.
- Ex4: Periodically conduct exercises of the product security incident response processes.

## RV.2.1 — RV.2 Assess, Prioritize, and Remediate Vulnerabilities
**Statement:** Analyze each vulnerability to gather sufficient information about risk to plan its remediation or other risk response.
- Ex1: Use existing issue tracking software to record each vulnerability.
- Ex2: Perform risk calculations for each vulnerability based on estimates of its exploitability, the potential impact if exploited, and any other relevant characteristics.

## RV.2.2 — RV.2 Assess, Prioritize, and Remediate Vulnerabilities
**Statement:** Plan and implement risk responses for vulnerabilities.
- Ex1: Make a risk-based decision as to whether each vulnerability will be remediated or if the risk will be addressed through other means (e.g., risk acceptance, risk transference), and prioritize any actions to be taken.
- Ex2: If a permanent mitigation for a vulnerability is not yet available, determine how the vulnerability can be temporarily mitigated until the permanent solution is available, and add that temporary remediation to the plan.
- Ex3: Develop and release security advisories that provide the necessary information to software acquirers, including descriptions of what the vulnerabilities are, how to find instances of the vulnerable software, and how to address them (e.g., where to get patches and what the patches change in the software; what configuration settings may need to be changed; how temporary workarounds could be implemented).
- Ex4: Deliver remediations to acquirers via an automated and trusted delivery mechanism. A single remediation could address multiple vulnerabilities.
- Ex5: Update records of design decisions, risk responses, and approved exceptions as needed. See PW.1.2.

## RV.3.1 — RV.3 Analyze Vulnerabilities to Identify Their Root Causes
**Statement:** Analyze identified vulnerabilities to determine their root causes.
- Ex1: Record the root cause of discovered issues.
- Ex2: Record lessons learned through root cause analysis in a wiki that developers can access and search.

## RV.3.2 — RV.3 Analyze Vulnerabilities to Identify Their Root Causes
**Statement:** Analyze the root causes over time to identify patterns, such as a particular secure coding practice not being followed consistently.
- Ex1: Record lessons learned through root cause analysis in a wiki that developers can access and search.
- Ex2: Add mechanisms to the toolchain to automatically detect future instances of the root cause.
- Ex3: Update manual processes to detect future instances of the root cause.

## RV.3.3 — RV.3 Analyze Vulnerabilities to Identify Their Root Causes
**Statement:** Review the software for similar vulnerabilities to eradicate a class of vulnerabilities, and proactively fix them rather than waiting for external reports.
- Ex1: See PW.7 and PW.8.

## RV.3.4 — RV.3 Analyze Vulnerabilities to Identify Their Root Causes
**Statement:** Review the SDLC process, and update it if appropriate to prevent (or reduce the likelihood of) the root cause recurring in updates to the software or in new software that is created.
- Ex1: Record lessons learned through root cause analysis in a wiki that developers can access and search.
- Ex2: Plan and implement changes to the appropriate SDLC practices.
