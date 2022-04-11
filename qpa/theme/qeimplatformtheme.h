#ifndef QEIM_PLATFORM_THEME_H
#define QEIM_PLATFORM_THEME_H

#include <QVariant>
#include <QFont>
#include <QPalette>
#include <qpa/qplatformtheme.h>

class QEimPlatformTheme : public QPlatformTheme
{
public:
    QEimPlatformTheme();
    virtual ~QEimPlatformTheme();

#if QT_CONFIG(shortcut)
    virtual QList<QKeySequence> keyBindings(QKeySequence::StandardKey key) const;
#endif
};

#endif // QEIM_PLATFORM_THEME_HH
