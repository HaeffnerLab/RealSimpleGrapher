from GraphWindow import GraphWindow

from PyQt5.QtWidgets import QApplication

if __name__ == '__main__':
    app = QApplication(sys.argv)
    import qt5reactor
    qt5reactor.install()
    from twisted.internet import reactor
    client = GraphWindow(reactor)
    client.setWindowTitle('RSG Client')
    client.show()
    app.exec_()
    #sys.exit(app.exec_())
    reactor.run()