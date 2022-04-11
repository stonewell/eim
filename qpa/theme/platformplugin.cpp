#include "platformplugin.h"

QEimPlatformThemePlugin::QEimPlatformThemePlugin(QObject *parent) : QPlatformThemePlugin(parent) { }

QPlatformTheme *QEimPlatformThemePlugin::create(const QString &key, const QStringList &paramList) {
    Q_UNUSED(paramList)
    if (key == "eim" || key == "qeimplatform")
        return new QEimPlatformTheme();
    return nullptr;
}
