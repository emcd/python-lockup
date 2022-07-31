.. vim: set fileencoding=utf-8:
.. -*- coding: utf-8 -*-
.. +--------------------------------------------------------------------------+
   |                                                                          |
   | Licensed under the Apache License, Version 2.0 (the "License");          |
   | you may not use this file except in compliance with the License.         |
   | You may obtain a copy of the License at                                  |
   |                                                                          |
   |     http://www.apache.org/licenses/LICENSE-2.0                           |
   |                                                                          |
   | Unless required by applicable law or agreed to in writing, software      |
   | distributed under the License is distributed on an "AS IS" BASIS,        |
   | WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. |
   | See the License for the specific language governing permissions and      |
   | limitations under the License.                                           |
   |                                                                          |
   +--------------------------------------------------------------------------+

.. include:: <isopub.txt>

*******************************************************************************
Requirements
*******************************************************************************

Commit Signatures
===============================================================================

All commits to the project must be signed with a valid GPG/PGP or S/MIME secret
key. You can use `GNU Privacy Guard <https://gnupg.org/>`_ or a similar tool to
generate a signing key if you do not already have one. And, you can likewise
use such a tool to sign your commits. Github has a good guide on the following
topics:

* `Commit Signature Verification
  <https://docs.github.com/en/authentication/managing-commit-signature-verification/about-commit-signature-verification>`_
* `GPG Key Generation
  <https://docs.github.com/en/authentication/managing-commit-signature-verification/generating-a-new-gpg-key>`_
* `GPG Key Registration on Github
  <https://docs.github.com/en/authentication/managing-commit-signature-verification/adding-a-gpg-key-to-your-github-account>`_
* `Git Client Configuration for Commit Signatures
  <https://docs.github.com/en/authentication/managing-commit-signature-verification/telling-git-about-your-signing-key>`_

If you do not wish to expose a personal email address in association with a
signing key, you can use the `no-reply email address
<https://docs.github.com/en/account-and-profile/setting-up-and-managing-your-personal-account-on-github/managing-email-preferences/setting-your-commit-email-address>`_
associated with your Github account instead.

In addition to registering the signature verification public key, which
corresponds to your secret signing key, with Github, you may also publish the
signature verification public key to well-known public key servers, such as:

* `MIT PGP Keyserver <https://pgp.mit.edu/>`_
* `Ubuntu Keyserver <https://keyserver.ubuntu.com/>`_

