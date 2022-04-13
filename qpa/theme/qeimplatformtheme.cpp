#include "qeimplatformtheme.h"

static
constexpr
QKeySequence::StandardKey filtered_Keys[] = {
  QKeySequence::Open,
  QKeySequence::Close,
  QKeySequence::Save,
  QKeySequence::New,
  QKeySequence::Cut,
  QKeySequence::Copy,
  QKeySequence::Paste,
  QKeySequence::Undo,
  QKeySequence::Redo,
  QKeySequence::Forward,
  QKeySequence::Refresh,
  QKeySequence::Find,
  QKeySequence::Replace,
  QKeySequence::SelectAll,
  QKeySequence::Bold,
  QKeySequence::Italic,
  QKeySequence::Underline,
  QKeySequence::MoveToNextWord,
  QKeySequence::MoveToPreviousWord,
  QKeySequence::MoveToStartOfBlock,
  QKeySequence::MoveToEndOfBlock,
  QKeySequence::DeleteEndOfLine,
  QKeySequence::SaveAs,
  QKeySequence::Preferences,
  QKeySequence::Quit,
  QKeySequence::Deselect,
  QKeySequence::DeleteCompleteLine,
};

const uint numberOfFilteredKeys = sizeof(filtered_Keys) /  sizeof(QKeySequence::StandardKey);

struct KeyBinding {
  QKeySequence::StandardKey standardKey;
  QKeyCombination key;
};

static
constexpr
KeyBinding key_Bindings[] = {
  {QKeySequence::Delete,                            Qt::Key_Delete},
  {QKeySequence::Back,                              Qt::Key_Backspace},
  {QKeySequence::FindNext,                          Qt::Key_F3},
  {QKeySequence::FindPrevious,                      Qt::SHIFT | Qt::Key_F3},
  {QKeySequence::MoveToNextChar,                    Qt::Key_Right},
  {QKeySequence::MoveToPreviousChar,                Qt::Key_Left},
  {QKeySequence::MoveToNextLine,                    Qt::Key_Down},
  {QKeySequence::MoveToPreviousLine,                Qt::Key_Up},
  {QKeySequence::MoveToNextPage,                    Qt::Key_PageDown},
  {QKeySequence::MoveToPreviousPage,                Qt::Key_PageUp},
  {QKeySequence::MoveToStartOfLine,                 Qt::Key_Home},
  {QKeySequence::MoveToEndOfLine,                   Qt::Key_End},
  {QKeySequence::MoveToStartOfDocument,             Qt::CTRL | Qt::Key_Home},
  {QKeySequence::MoveToEndOfDocument,               Qt::CTRL | Qt::Key_End},
  {QKeySequence::SelectNextChar,                    Qt::SHIFT | Qt::Key_Right},
  {QKeySequence::SelectPreviousChar,                Qt::SHIFT | Qt::Key_Left},
  {QKeySequence::SelectNextWord,                    Qt::CTRL | Qt::SHIFT | Qt::Key_Right},
  {QKeySequence::SelectPreviousWord,                Qt::CTRL | Qt::SHIFT | Qt::Key_Left},
  {QKeySequence::SelectStartOfDocument,             Qt::CTRL | Qt::SHIFT | Qt::Key_Home},
  {QKeySequence::SelectEndOfDocument,               Qt::CTRL | Qt::SHIFT | Qt::Key_End},

  {QKeySequence::InsertParagraphSeparator,          Qt::Key_Enter},
  {QKeySequence::InsertParagraphSeparator,          Qt::Key_Return},
  {QKeySequence::InsertLineSeparator,               Qt::SHIFT | Qt::Key_Enter},
  {QKeySequence::InsertLineSeparator,               Qt::SHIFT | Qt::Key_Return},
};

const uint numberOfKeyBindings = sizeof(key_Bindings) /  sizeof(KeyBinding);

QEimPlatformTheme::QEimPlatformTheme()
{
}

QEimPlatformTheme::~QEimPlatformTheme()
{
}

QList<QKeySequence> QEimPlatformTheme::keyBindings(QKeySequence::StandardKey key) const
{
  const char * env_key = QString("StandardKey_%1").arg(key).toUtf8();
  QString env = qEnvironmentVariable(env_key, "");

  for (uint i = 0; i < numberOfFilteredKeys; i++) {
    if (filtered_Keys[i] == key) {
      QList <QKeySequence> list;

      if (env != "") {
        list.append(QKeySequence(env));
      }

      return list;
    }
  }

  QList <QKeySequence> list;
  bool forced = false;

  for (uint i = 0; i < numberOfKeyBindings; i++) {
    if (key_Bindings[i].standardKey == key) {
      list.append(QKeySequence(key_Bindings[i].key.toCombined()));

      forced = true;
    }
  }

  if (forced) {
    if (env != "") {
      list.prepend(QKeySequence(env));
    }

    return list;
  }

  return QPlatformTheme::keyBindings(key);
}
