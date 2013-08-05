Name: pyqt-mail-checker
Version: 2.0.2
Release: 3%{?dist}
Summary: Applet periodically checking for new messages in the mailboxes
Summary(ru): Апплет периодически проверяет наличие новых писем в списке почтовых ящиков
Group: Applications/Internet
License: GPLv2+
Source0: https://github.com/F1ash/%{name}/archive/%{version}.tar.gz
URL: https://github.com/F1ash/%{name}
BuildArch: noarch

Requires: python-SocksiPy, python-mailer, python-crypto
Requires: PyQt4, sound-theme-freedesktop
# for building the translator`s dictionary
BuildRequires: qt4-devel
# for validate the .desktop file
BuildRequires: desktop-file-utils

%description
Applet should periodic check for new messages in configured accounts
and show mail headers in notification.
Supported protocols: POP3/POP3S/IMAP4/IMAP4S + IMAP4_IDLE.
Passwords for accounts stored in encrypted container
(KWallet / Gnome Keyring / Crypto File).
Support integrated mail viewer with quick answer & forward mail.

%description -l ru
Апплет периодически проверяет наличие новых писем
(с момента последней проверки) в списке почтовых ящиков
и показывает заголовки новой почты в нотификации.
Поддерживаются POP3\IMAP4(+IDLE) протоколы с None\SSL аутентификацией.
Пароли к почтовым ящикам содержатся в зашифрованном виде
(KWallet / Gnome Keyring / Crypto File).
Есть встроенный предпросмотр почты с возможностью
быстрого ответа и пересылки.

%prep
%setup -q

%build
# nothing to build

%install
make install DESTDIR=%{buildroot}/%{_prefix}
desktop-file-validate %{buildroot}/%{_datadir}/applications/%{name}.desktop

%files
%{_bindir}/%{name}
%{_datadir}/applications/%{name}.desktop
%{_datadir}/%{name}
%{_datadir}/icons/hicolor/32x32/apps/mailChecker*
%doc README README_RU COPYING Changelog Licenses

%post
/bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null || :

%postun
if [ $1 -eq 0 ] ; then
    /bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null
    /usr/bin/gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :
fi

%posttrans
/usr/bin/gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :

%changelog
* Mon Aug  5 2013 Fl@sh <kaperang07@gmail.com> - 2.0.2-3
- Summary fixed;
- release number changed

* Wed Jul 31 2013 Fl@sh <kaperang07@gmail.com> - 2.0.2-2
- fixed binary file name;
- release number changed

* Mon Jul 29 2013 Fl@sh <kaperang07@gmail.com> - 2.0.2-1
- description extended;
- version updated

* Thu Jul 18 2013 Fl@sh <kaperang07@gmail.com> - 2.0.1-4
- fixed install tag to macros-style;
- release number changed

* Wed Jul 17 2013 Fl@sh <kaperang07@gmail.com> - 2.0.1-3
- added the desktop-file-validate scriptlet;
- release number changed

* Wed Jul 17 2013 Fl@sh <kaperang07@gmail.com> - 2.0.1-2
- added the icon-cache-update scriptlet with build require;
- release number changed

* Fri Jul 12 2013 Fl@sh <kaperang07@gmail.com> - 2.0.1-1
- version updated

* Tue Jun 11 2013 Fl@sh <kaperang07@gmail.com> - 2.0.0-1
- version updated

* Wed Apr 24 2013 Fl@sh <kaperang07@gmail.com> - 1.12.55-1
- Initial build
