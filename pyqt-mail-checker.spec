Name: pyqt-mail-checker
Version: 1.12.55
Release: 1%{?dist}
Summary: Tray applet for periodically checking a new messages in the mailboxes list
Summary(ru): Апплет периодически проверяет наличие новых писем в списке почтовых ящиков
Group: Applications/Internet
License: GPLv2+
Source0: https://github.com/F1ash/%{name}/archive/%{version}.tar.gz
URL: https://github.com/F1ash/%{name}
BuildArch: noarch

Requires: python-SocksiPy, python-mailer, PyQt4
# for building the translator`s dictionary
BuildRequires: qt4-devel

%description
%{name}
Applet should periodic check for new messages in configured accounts.
Supported protocols: POP3/POP3S/IMAP4/IMAP4S + IMAP4_IDLE.
Passwords for accounts stored in encrypted container.
Support preview (integrated mail viewer) and Quick Answer & Forward Mail.

%description -l ru
%{name}
Апплет периодически проверяет наличие новых писем
в списке почтовых ящиков.
Поддерживаются POP3\IMAP4(+IDLE) протоколы с None\SSL аутентификацией.
Пароли к почтовым ящикам содержатся в зашифрованном виде.
Есть встроенный предпросмотр почты с возможностью
быстрого ответа и пересылки.

%prep
%setup -q

%build

%install
make install DESTDIR=$RPM_BUILD_ROOT/usr

%files
%{_bindir}/%{name}.py
%{_desktopdir}/%{name}.desktop
%{_datadir}/%{name}
%{_iconsdir}/hicolor/32x32/apps/mailChecker*
%doc README README_RU COPYING Changelog Licenses

%changelog
* Wed Apr 24 2013 Fl@sh <kaperang07@gmail.com> - 1.12.55-1
- Initial build
